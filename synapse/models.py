# synapse/models.py

from django.db import models
from django.utils import timezone

#
# 1) Neurotransmitter & neuromodulator pools
#

class SynapticCleft(models.Model):
    """
    Vesicular glutamate release and reuptake/diffusion.
    """
    glutamate  = models.FloatField(default=0.0)  # mM
    clear_rate = models.FloatField(default=0.5)  # mM per tick

    # Presynaptic activity tracking fields
    last_spike_time = models.DateTimeField(null=True, blank=True)
    spike_count = models.IntegerField(default=0)
    spike_history = models.JSONField(default=list, blank=True)

    def release(self, amount: float = 1.2):
        """
        Add a fixed amount of glutamate to the cleft, simulating vesicular release.
        """
        self.glutamate += amount
        self.save()

    def clear(self):
        """
        Remove glutamate from the cleft at the set clearance rate, simulating reuptake and diffusion.
        """
        self.glutamate = max(0.0, self.glutamate - self.clear_rate)
        self.save()

    def noisy_release(self, amount: float = 1.2, noise_std: float = 0.1):
        """
        Add glutamate to the cleft with Gaussian noise, simulating stochastic vesicle release.
        """
        import random
        noisy_amount = amount + random.gauss(0, noise_std)
        self.glutamate += max(0.0, noisy_amount)
        self.save()

    def record_spike(self):
        """
        Record a presynaptic spike event: update last spike time, increment count, and log timestamp.
        """
        now = timezone.now()
        self.last_spike_time = now
        self.spike_count += 1
        self.spike_history.append(str(now))
        self.save()

    def recent_spike_count(self, window_sec: float = 1.0):
        """
        Return the number of spikes in the last 'window_sec' seconds.
        """
        now = timezone.now()
        return sum(
            (now - timezone.datetime.fromisoformat(ts)).total_seconds() <= window_sec
            for ts in self.spike_history
        )


class DopamineCleft(models.Model):
    """
    Phasic dopamine bursts and transporter-mediated clearance.
    """
    dopamine   = models.FloatField(default=0.0)  # mM
    clear_rate = models.FloatField(default=0.1)  # mM per tick

    def release(self, amount: float = 0.8):
        """
        Add a fixed amount of dopamine to the cleft, simulating phasic release.
        """
        self.dopamine += amount
        self.save()

    def clear(self):
        """
        Remove dopamine from the cleft at the set clearance rate, simulating transporter action.
        """
        self.dopamine = max(0.0, self.dopamine - self.clear_rate)
        self.save()


#
# 2) Receptors & second-messenger cascades
#

class NMDAReceptor(models.Model):
    """
    NMDA channel: Mg²⁺-blocked ↔ open based on glutamate & Vm.
    """
    mg_blocked    = models.BooleanField(default=True)
    glutamate_thr = models.FloatField(default=1.0)    # mM
    voltage_thr   = models.FloatField(default=-50.0)  # mV

    def try_open(self, cleft: SynapticCleft, membrane: 'PostSynapticMembrane') -> bool:
        """
        Attempt to open the NMDA channel if glutamate and depolarization thresholds are met.
        Returns True if channel opens (Mg2+ block removed).
        """
        if (cleft.glutamate >= self.glutamate_thr and
            membrane.potential >= self.voltage_thr):
            self.mg_blocked = False
            self.save()
            return True
        return False

    def reset(self):
        """
        Restore Mg2+ block, closing the NMDA channel.
        """
        self.mg_blocked = True
        self.save()

    def ca_conductance(self) -> float:
        """
        Return the fixed calcium conductance for an open NMDA channel.
        """
        return 0.2


class DopamineReceptor(models.Model):
    """
    D1/D2 receptor: binds dopamine to gate cAMP/PKA.
    """
    bound = models.BooleanField(default=False)
    kd    = models.FloatField(default=0.5)  # mM

    def try_bind(self, cleft: DopamineCleft) -> bool:
        """
        Attempt to bind dopamine if concentration exceeds dissociation constant (Kd).
        Returns True if binding occurs.
        """
        if cleft.dopamine >= self.kd:
            self.bound = True
            self.save()
            return True
        return False

    def unbind(self):
        """
        Unbind dopamine from the receptor.
        """
        self.bound = False
        self.save()


class ModulatoryCascade(models.Model):
    """
    cAMP/PKA cascade state; modulates Ca²⁺ sensitivity.
    """
    camp         = models.FloatField(default=0.0)
    pka_activity = models.FloatField(default=0.0)

    def activate(self):
        """
        Activate the cAMP/PKA cascade, increasing cAMP and updating PKA activity.
        """
        self.camp += 1.0
        self.pka_activity = 1.0 / (1.0 + 2.71828 ** (-(self.camp - 1.0)))
        self.save()


#
# 3) Electrical substrate & local Ca²⁺ store
#

class PostSynapticMembrane(models.Model):
    """
    Spine-head membrane potential; depolarizes via back-propagating AP.
    """
    rest_potential = models.FloatField(default=-70.0)  # mV
    potential      = models.FloatField(default=-70.0)  # mV
    depolarization = models.FloatField(default=20.0)   # mV

    def depolarize(self):
        """
        Set the membrane potential to a depolarized value (simulating a back-propagating action potential).
        """
        self.potential = self.rest_potential + self.depolarization
        self.save()

    def reset(self):
        """
        Restore the membrane potential to its resting value.
        """
        self.potential = self.rest_potential
        self.save()


class SpineHead(models.Model):
    """
    Postsynaptic spine: local [Ca²⁺] & PKA-modulated sensitivity.
    """
    ca_concentration = models.FloatField(default=0.0)  # µM
    ca_sensitivity   = models.FloatField(default=1.0)  # multiplier

    def influx(self, amount: float):
        """
        Increase local calcium concentration in the spine head by a given amount.
        """
        self.ca_concentration += amount
        self.save()

    def clear_ca(self):
        """
        Reset calcium concentration to zero (simulating rapid clearance after a spike).
        """
        self.ca_concentration = 0.0
        self.save()

    def modulate_sensitivity(self, pka_activity: float):
        """
        Adjust calcium sensitivity based on PKA activity (modulatory effect).
        """
        self.ca_sensitivity = 1.0 + 0.5 * pka_activity
        self.save()

    def buffer_and_pump(self, buffer_capacity: float = 2.0, pump_rate: float = 0.2):
        """
        Limit free calcium by buffering and simulate extrusion via pumps.
        """
        if self.ca_concentration > buffer_capacity:
            self.ca_concentration = buffer_capacity
        self.ca_concentration = max(0.0, self.ca_concentration - pump_rate)
        self.save()

    def grow(self, delta: float = 0.1):
        """
        Increase spine sensitivity, simulating structural growth (enlargement).
        """
        self.ca_sensitivity += delta
        self.save()

    def shrink(self, delta: float = 0.1):
        """
        Decrease spine sensitivity, simulating shrinkage or loss.
        """
        self.ca_sensitivity = max(0.1, self.ca_sensitivity - delta)
        self.save()


#
# 4) STDP parameters & tagging
#

class STDPParameters(models.Model):
    """
    Thresholds & rates for Ca²⁺-dependent LTP vs LTD.
    """
    ltp_threshold = models.FloatField(default=5.0)
    ltd_threshold = models.FloatField(default=1.0)
    ltp_rate      = models.FloatField(default=0.01)
    ltd_rate      = models.FloatField(default=0.005)

    def metaplasticity_update(self, recent_activity: float, target_activity: float = 20.0, eta: float = 0.01):
        """
        Adjust LTP/LTD thresholds based on recent activity (sliding threshold metaplasticity).
        """
        delta = recent_activity - target_activity
        self.ltp_threshold += eta * delta
        self.ltd_threshold += eta * delta * 0.5
        self.save()


class SynapticTag(models.Model):
    """
    Marks a synapse active during wake for later consolidation.
    """
    tagged      = models.BooleanField(default=False)
    time_tagged = models.DateTimeField(null=True, blank=True)

    def set(self):
        """
        Mark the synapse as tagged and record the current time (for consolidation).
        """
        self.tagged      = True
        self.time_tagged = timezone.now()
        self.save()

    def clear(self):
        """
        Remove the tag and clear the timestamp.
        """
        self.tagged      = False
        self.time_tagged = None
        self.save()


class ConsolidationProteinPool(models.Model):
    """
    Pool of proteins (BDNF, Arc) for tagged-synapse consolidation.
    """
    available     = models.IntegerField(default=100)
    last_refilled = models.DateTimeField(auto_now=True)

    def consume(self) -> bool:
        """
        Use one consolidation protein if available. Returns True if successful.
        """
        if self.available > 0:
            self.available -= 1
            self.save()
            return True
        return False


#
# 5) AMPA receptor pools & trafficking rates
#

class AMPARecyclingEndosome(models.Model):
    """
    Reserve pool of AMPARs for insertion.
    """
    pool_count = models.IntegerField(default=100)

    def remove(self, count: int) -> int:
        """
        Remove up to 'count' AMPARs from the endosome pool. Returns number actually removed.
        """
        actual = min(self.pool_count, count)
        self.pool_count -= actual
        self.save()
        return actual

    def add(self, count: int):
        """
        Add AMPARs to the endosome pool.
        """
        self.pool_count += count
        self.save()


class PostSynapticDensity(models.Model):
    """
    AMPARs currently at the postsynaptic density.
    """
    ampa_count = models.IntegerField(default=20)

    def add(self, count: int):
        """
        Add AMPARs to the postsynaptic density.
        """
        self.ampa_count += count
        self.save()

    def remove(self, count: int) -> int:
        """
        Remove up to 'count' AMPARs from the postsynaptic density. Returns number actually removed.
        """
        actual = min(self.ampa_count, count)
        self.ampa_count -= actual
        self.save()
        return actual


class TraffickingParameters(models.Model):
    """
    Rates for LTP insertion vs LTD removal.
    """
    insertion_rate = models.FloatField(default=5.0)
    removal_rate   = models.FloatField(default=5.0)

    def compute_insertion(self, delta_w: float) -> int:
        """
        Compute number of AMPARs to insert for a given weight change.
        """
        return int(delta_w * self.insertion_rate)

    def compute_removal(self, delta_w: float) -> int:
        """
        Compute number of AMPARs to remove for a given weight change.
        """
        return int(abs(delta_w) * self.removal_rate)


#
# 6) Astrocyte‐mediated homeostasis
#

class Astrocyte(models.Model):
    """
    Senses network activity and releases gliotransmitters.
    """
    monitored_activity = models.FloatField(default=0.0)
    tnf_alpha          = models.FloatField(default=0.0)
    d_serine           = models.FloatField(default=0.0)
    atp                = models.FloatField(default=0.0)
    release_rate       = models.FloatField(default=0.1)

    def sense_activity(self, activity: float):
        """
        Update monitored activity and adjust gliotransmitter levels in response to network activity.
        """
        self.monitored_activity = activity
        self.tnf_alpha += self.release_rate * (1.0 - activity)
        self.d_serine  += self.release_rate * max(activity - 0.5, 0.0)
        self.atp       += self.release_rate * max(activity - 1.0, 0.0)
        self.save()

    def clear_transmitters(self):
        """
        Gradually clear gliotransmitters from the astrocyte (decay toward zero).
        """
        for field in ('tnf_alpha', 'd_serine', 'atp'):
            val = getattr(self, field)
            setattr(self, field, max(0.0, val - self.release_rate))
        self.save()

    def modulate_synapse(self, synapse, tnf_alpha_effect: float = 0.01, d_serine_effect: float = 0.01):
        """
        Modulate synaptic weight and sensitivity based on astrocyte gliotransmitter levels.
        """
        synapse.weight += self.tnf_alpha * tnf_alpha_effect
        synapse.spine.ca_sensitivity += self.d_serine * d_serine_effect
        synapse.save()
        synapse.spine.save()


#
# 7) Synapse linkage (no orchestration methods here)
#

class Synapse(models.Model):
    """
    Groups all biochemical components for one synapse.
    Orchestration belongs in a service or view layer.
    """
    cleft        = models.ForeignKey(SynapticCleft,        on_delete=models.CASCADE)
    da_cleft     = models.ForeignKey(DopamineCleft,        on_delete=models.CASCADE)
    membrane     = models.ForeignKey(PostSynapticMembrane, on_delete=models.CASCADE)
    nmda         = models.ForeignKey(NMDAReceptor,         on_delete=models.CASCADE)
    da_receptor  = models.ForeignKey(DopamineReceptor,     on_delete=models.CASCADE)
    cascade      = models.ForeignKey(ModulatoryCascade,    on_delete=models.CASCADE)
    spine        = models.OneToOneField(SpineHead,         on_delete=models.CASCADE)
    stdp_params  = models.ForeignKey(STDPParameters,       on_delete=models.CASCADE)
    tag          = models.OneToOneField(SynapticTag,       on_delete=models.CASCADE)
    pool         = models.OneToOneField(ConsolidationProteinPool,
                                        on_delete=models.CASCADE)
    endosome     = models.OneToOneField(AMPARecyclingEndosome,
                                        on_delete=models.CASCADE)
    psd          = models.OneToOneField(PostSynapticDensity,
                                        on_delete=models.CASCADE)
    traf_params  = models.ForeignKey(TraffickingParameters,
                                     on_delete=models.CASCADE)
    astrocyte    = models.ForeignKey(Astrocyte,             on_delete=models.CASCADE)

    weight       = models.FloatField(default=1.0)  # synaptic efficacy
    last_plasticity_time = models.DateTimeField(null=True, blank=True)
    history_log = models.JSONField(default=list, blank=True)

    def __str__(self):
        return f"Synapse {self.pk} (w={self.weight:.2f})"

    def synaptic_scaling(self, target_activity: float = 20.0, eta: float = 0.001):
        """
        Adjust synaptic weight to maintain activity near a target value (homeostatic scaling).
        """
        current = self.psd.ampa_count
        scale = 1.0 + eta * (target_activity - current)
        self.weight *= scale
        self.save()

    def eliminate(self):
        """
        Set synaptic weight to zero, marking the synapse as pruned/eliminated.
        """
        self.weight = 0.0
        self.save()

    def form(self, initial_weight: float = 1.0):
        """
        Restore or create a synapse with a given initial weight.
        """
        self.weight = initial_weight
        self.save()

    def noisy_weight_update(self, dw: float, noise_std: float = 0.001):
        """
        Update synaptic weight with added Gaussian noise (stochastic plasticity).
        """
        import random
        noisy_dw = dw + random.gauss(0, noise_std)
        self.weight += noisy_dw
        self.save()

    def log_event(self, event: str):
        """
        Record a plasticity event with timestamp in the synapse's history log.
        """
        from django.utils import timezone
        self.last_plasticity_time = timezone.now()
        self.history_log.append({'time': str(self.last_plasticity_time), 'event': event})
        self.save()
