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

    def release(self, amount: float = 1.2):
        self.glutamate += amount
        self.save()

    def clear(self):
        self.glutamate = max(0.0, self.glutamate - self.clear_rate)
        self.save()


class DopamineCleft(models.Model):
    """
    Phasic dopamine bursts and transporter-mediated clearance.
    """
    dopamine   = models.FloatField(default=0.0)  # mM
    clear_rate = models.FloatField(default=0.1)  # mM per tick

    def release(self, amount: float = 0.8):
        self.dopamine += amount
        self.save()

    def clear(self):
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
        if (cleft.glutamate >= self.glutamate_thr and
            membrane.potential >= self.voltage_thr):
            self.mg_blocked = False
            self.save()
            return True
        return False

    def reset(self):
        self.mg_blocked = True
        self.save()

    def ca_conductance(self) -> float:
        return 0.2


class DopamineReceptor(models.Model):
    """
    D1/D2 receptor: binds dopamine to gate cAMP/PKA.
    """
    bound = models.BooleanField(default=False)
    kd    = models.FloatField(default=0.5)  # mM

    def try_bind(self, cleft: DopamineCleft) -> bool:
        if cleft.dopamine >= self.kd:
            self.bound = True
            self.save()
            return True
        return False

    def unbind(self):
        self.bound = False
        self.save()


class ModulatoryCascade(models.Model):
    """
    cAMP/PKA cascade state; modulates Ca²⁺ sensitivity.
    """
    camp         = models.FloatField(default=0.0)
    pka_activity = models.FloatField(default=0.0)

    def activate(self):
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
        self.potential = self.rest_potential + self.depolarization
        self.save()

    def reset(self):
        self.potential = self.rest_potential
        self.save()


class SpineHead(models.Model):
    """
    Postsynaptic spine: local [Ca²⁺] & PKA-modulated sensitivity.
    """
    ca_concentration = models.FloatField(default=0.0)  # µM
    ca_sensitivity   = models.FloatField(default=1.0)  # multiplier

    def influx(self, amount: float):
        self.ca_concentration += amount
        self.save()

    def clear_ca(self):
        self.ca_concentration = 0.0
        self.save()

    def modulate_sensitivity(self, pka_activity: float):
        self.ca_sensitivity = 1.0 + 0.5 * pka_activity
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


class SynapticTag(models.Model):
    """
    Marks a synapse active during wake for later consolidation.
    """
    tagged      = models.BooleanField(default=False)
    time_tagged = models.DateTimeField(null=True, blank=True)

    def set(self):
        self.tagged      = True
        self.time_tagged = timezone.now()
        self.save()

    def clear(self):
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
        actual = min(self.pool_count, count)
        self.pool_count -= actual
        self.save()
        return actual

    def add(self, count: int):
        self.pool_count += count
        self.save()


class PostSynapticDensity(models.Model):
    """
    AMPARs currently at the postsynaptic density.
    """
    ampa_count = models.IntegerField(default=20)

    def add(self, count: int):
        self.ampa_count += count
        self.save()

    def remove(self, count: int) -> int:
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
        return int(delta_w * self.insertion_rate)

    def compute_removal(self, delta_w: float) -> int:
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
        self.monitored_activity = activity
        self.tnf_alpha += self.release_rate * (1.0 - activity)
        self.d_serine  += self.release_rate * max(activity - 0.5, 0.0)
        self.atp       += self.release_rate * max(activity - 1.0, 0.0)
        self.save()

    def clear_transmitters(self):
        for field in ('tnf_alpha', 'd_serine', 'atp'):
            val = getattr(self, field)
            setattr(self, field, max(0.0, val - self.release_rate))
        self.save()


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

    def __str__(self):
        return f"Synapse {self.pk} (w={self.weight:.2f})"
