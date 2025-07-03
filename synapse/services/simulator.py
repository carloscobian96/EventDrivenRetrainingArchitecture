from synapse.models import Synapse

class SynapseSimulator:
    def __init__(self, synapse: Synapse):
        self.s = synapse

    def tick(self):
        # 1) Release & clear transmitters
        self.s.cleft.release()
        self.s.da_cleft.release()
        self.s.cleft.clear()
        self.s.da_cleft.clear()

        # 2) Update membrane & NMDA
        opened = self.s.nmda.try_open(self.s.cleft, self.s.membrane)
        if opened:
            ca_in = self.s.nmda.ca_conductance() * self.s.spine.ca_sensitivity
            self.s.spine.influx(ca_in)
        self.s.membrane.depolarize()

        # 3) Dopamine binding & cascade
        bound = self.s.da_receptor.try_bind(self.s.da_cleft)
        if bound:
            self.s.cascade.activate()
        else:
            self.s.da_receptor.unbind()

        # 4) STDP weight update
        ca = self.s.spine.ca_concentration
        params = self.s.stdp_params
        if ca >= params.ltp_threshold:
            dw = params.ltp_rate
        elif ca <= params.ltd_threshold:
            dw = -params.ltd_rate
        else:
            dw = 0.0
        self.s.weight += dw
        self.s.save()

        # 5) AMPA trafficking
        tp = self.s.traf_params
        if dw > 0:
            ins = tp.compute_insertion(dw)
            moved = self.s.endosome.remove(ins)
            self.s.psd.add(moved)
        elif dw < 0:
            rem = tp.compute_removal(dw)
            moved = self.s.psd.remove(rem)
            self.s.endosome.add(moved)

        # 6) Tag & consolidation
        if abs(dw) >= params.ltp_rate:
            self.s.tag.set()
            self.s.pool.consume()

        # 7) Homeostasis & cleanup
        activity = self.s.psd.ampa_count  # or any proxy
        self.s.astrocyte.sense_activity(activity)
        self.s.spine.clear_ca()
        self.s.nmda.reset()
        self.s.membrane.reset()
