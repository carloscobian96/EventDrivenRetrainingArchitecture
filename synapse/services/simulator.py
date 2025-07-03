from synapse.models import Synapse

class SynapseSimulator:
    def __init__(self, synapse: Synapse):
        self.s = synapse

    def tick(self):
        """
        Advance the synapse simulation by one time step.
        This models the sequence of events in a single synaptic cycle, including:
        1. Presynaptic spike tracking and transmitter release (with noise option)
        2. Postsynaptic membrane and receptor updates (with PKA modulation)
        3. Dopaminergic modulation
        4. Calcium and STDP-based plasticity (optionally noisy, with event logging)
        5. AMPA receptor trafficking
        6. Tagging and consolidation
        7. Homeostasis, metaplasticity, synaptic scaling, and glial modulation
        8. Structural plasticity (optional, e.g., spine growth/shrink)
        """
        # 1) Presynaptic spike tracking and transmitter release
        self.s.cleft.record_spike()  # Track presynaptic spike
        # Use noisy release for more biological realism
        self.s.cleft.noisy_release()  # You can switch to .release() if you want deterministic
        self.s.da_cleft.release()
        self.s.cleft.clear()
        self.s.da_cleft.clear()

        # 2) Update membrane & NMDA
        opened = self.s.nmda.try_open(self.s.cleft, self.s.membrane)
        if opened:
            ca_in = self.s.nmda.ca_conductance() * self.s.spine.ca_sensitivity
            self.s.spine.influx(ca_in)
        self.s.membrane.depolarize()

        # 2b) Calcium buffering/pump
        self.s.spine.buffer_and_pump()

        # 2c) PKA modulation of calcium sensitivity (if cascade is active)
        self.s.spine.modulate_sensitivity(self.s.cascade.pka_activity)

        # 3) Dopamine binding & cascade
        bound = self.s.da_receptor.try_bind(self.s.da_cleft)
        if bound:
            self.s.cascade.activate()
        else:
            self.s.da_receptor.unbind()

        # 4) STDP weight update (optionally use presynaptic activity)
        ca = self.s.spine.ca_concentration
        params = self.s.stdp_params
        pre_spikes = self.s.cleft.recent_spike_count(window_sec=1.0)
        # Example: Use noisy weight update for stochasticity
        if ca >= params.ltp_threshold:
            dw = params.ltp_rate
        elif ca <= params.ltd_threshold:
            dw = -params.ltd_rate
        else:
            dw = 0.0
        self.s.noisy_weight_update(dw)  # Use noisy update for biological realism
        self.s.log_event(f"Weight update: {dw}, PreSpikes: {pre_spikes}, Ca: {ca:.3f}")

        # 5) AMPA trafficking
        tp = self.s.traf_params
        if dw > 0:
            ins = tp.compute_insertion(dw)
            moved = self.s.endosome.remove(ins)
            self.s.psd.add(moved)
            # Optional: structural growth if strong LTP
            if dw > 0.5 * params.ltp_rate:
                self.s.spine.grow(0.05)
        elif dw < 0:
            rem = tp.compute_removal(dw)
            moved = self.s.psd.remove(rem)
            self.s.endosome.add(moved)
            # Optional: structural shrinkage if strong LTD
            if dw < -0.5 * params.ltd_rate:
                self.s.spine.shrink(0.05)

        # 6) Tag & consolidation
        if abs(dw) >= params.ltp_rate:
            self.s.tag.set()
            self.s.pool.consume()

        # 7) Homeostasis & cleanup
        activity = self.s.psd.ampa_count  # or any proxy
        self.s.astrocyte.sense_activity(activity)
        # Glial modulation of synapse (astrocyte effect)
        self.s.astrocyte.modulate_synapse(self.s)
        # Metaplasticity: update thresholds based on activity
        self.s.stdp_params.metaplasticity_update(activity)
        # Synaptic scaling: adjust weight to keep activity near target
        self.s.synaptic_scaling()
        self.s.spine.clear_ca()
        self.s.nmda.reset()
        self.s.membrane.reset()
        # Optional: prune synapse if weight is very low
        if self.s.weight < 0.01:
            self.s.eliminate()
            self.s.log_event("Synapse eliminated (pruned)")
        # Optional: form synapse if weight is restored
        if self.s.weight > 0.1 and self.s.last_plasticity_time is not None:
            self.s.form(initial_weight=self.s.weight)
            self.s.log_event("Synapse formed/reactivated")
