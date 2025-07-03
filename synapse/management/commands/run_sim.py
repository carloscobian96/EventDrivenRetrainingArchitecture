from django.core.management.base import BaseCommand
from synapse.models import Synapse
from synapse.services.simulator import SynapseSimulator

class Command(BaseCommand):
    help = "Run synapse simulation ticks"

    def add_arguments(self, parser):
        parser.add_argument('synapse_id', type=int)
        parser.add_argument('--ticks', type=int, default=1)

    def handle(self, *args, **opts):
        s = Synapse.objects.get(pk=opts['synapse_id'])
        sim = SynapseSimulator(s)
        for i in range(opts['ticks']):
            sim.tick()
            self.stdout.write(f"Tick {i+1}: weight={s.weight:.3f}")
