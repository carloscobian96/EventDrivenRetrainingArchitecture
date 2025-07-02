from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.shortcuts import redirect

from django.shortcuts import render
from .models import Synapse

@csrf_exempt
@require_http_methods(["GET", "POST"])
def plasticity_diagram(request):
    """Render the static plasticity cascade diagram page."""
    return render(request, 'synapse/plasticity_diagram.html')


@csrf_exempt
@require_http_methods(["GET", "POST"])
def plasticity_report(request):
    syn = Synapse.objects.first()
    # Map action names to callables (lambda or function) in a list for ordering
    ACTIONS = [
        ('cleft_release',      lambda post: syn.cleft.release(float(post.get('amount', 1.2)))),
        ('cleft_clear',        lambda post: syn.cleft.clear()),
        ('da_release',         lambda post: syn.da_cleft.release(float(post.get('amount', 0.8)))),
        ('da_clear',           lambda post: syn.da_cleft.clear()),
        ('nmda_reset',         lambda post: syn.nmda.reset()),
        # try_open: handled below
        ('da_unbind',          lambda post: syn.da_receptor.unbind()),
        # try_bind: handled below
        ('cascade_activate',   lambda post: syn.cascade.activate()),
        ('membrane_depolarize',lambda post: syn.membrane.depolarize()),
        ('membrane_reset',     lambda post: syn.membrane.reset()),
        ('spine_influx',       lambda post: syn.spine.influx(float(post.get('amount', 1.0)))),
        ('spine_clear_ca',     lambda post: syn.spine.clear_ca()),
        ('spine_modulate_sensitivity', lambda post: syn.spine.modulate_sensitivity(float(post.get('pka_activity', 1.0)))),
        ('tag_set',            lambda post: syn.tag.set()),
        ('tag_clear',          lambda post: syn.tag.clear()),
        ('pool_consume',       lambda post: syn.pool.consume()),
        ('endosome_remove',    lambda post: syn.endosome.remove(int(post.get('count', 1)))),
        ('endosome_add',       lambda post: syn.endosome.add(int(post.get('count', 1)))),
        ('psd_add',            lambda post: syn.psd.add(int(post.get('count', 1)))),
        ('psd_remove',         lambda post: syn.psd.remove(int(post.get('count', 1)))),
        ('trafficking_compute_insertion', lambda post: syn.traffickingparams.compute_insertion(float(post.get('delta_w', 1.0)))),
        ('trafficking_compute_removal',   lambda post: syn.traffickingparams.compute_removal(float(post.get('delta_w', 1.0)))),
        ('astrocyte_sense_activity',      lambda post: syn.astrocyte.sense_activity(float(post.get('activity', 1.0)))),
        ('astrocyte_clear_transmitters',  lambda post: syn.astrocyte.clear_transmitters()),
    ]
    ACTIONS_DICT = dict(ACTIONS)

    # --- Computed/derived values for UI (only real model attributes) ---
    computed = {}
    # SynapticCleft
    computed['cleft_glutamate'] = getattr(syn.cleft, 'glutamate', None)
    # DopamineCleft
    computed['da_cleft_dopamine'] = getattr(syn.da_cleft, 'dopamine', None)
    # NMDAReceptor
    computed['nmda_mg_blocked'] = getattr(syn.nmda, 'mg_blocked', None)
    computed['nmda_glutamate_thr'] = getattr(syn.nmda, 'glutamate_thr', None)
    computed['nmda_voltage_thr'] = getattr(syn.nmda, 'voltage_thr', None)
    # DopamineReceptor
    computed['da_receptor_bound'] = getattr(syn.da_receptor, 'bound', None)
    computed['da_receptor_kd'] = getattr(syn.da_receptor, 'kd', None)
    # ModulatoryCascade
    computed['cascade_camp'] = getattr(syn.cascade, 'camp', None)
    computed['cascade_pka_activity'] = getattr(syn.cascade, 'pka_activity', None)
    # PostSynapticMembrane
    computed['membrane_potential'] = getattr(syn.membrane, 'potential', None)
    computed['membrane_rest_potential'] = getattr(syn.membrane, 'rest_potential', None)
    computed['membrane_depolarization'] = getattr(syn.membrane, 'depolarization', None)
    # SpineHead
    computed['spine_ca_concentration'] = getattr(syn.spine, 'ca_concentration', None)
    computed['spine_ca_sensitivity'] = getattr(syn.spine, 'ca_sensitivity', None)
    # STDPParameters
    computed['ltp_threshold'] = getattr(syn.stdp_params, 'ltp_threshold', None)
    computed['ltd_threshold'] = getattr(syn.stdp_params, 'ltd_threshold', None)
    computed['ltp_rate'] = getattr(syn.stdp_params, 'ltp_rate', None)
    computed['ltd_rate'] = getattr(syn.stdp_params, 'ltd_rate', None)
    # SynapticTag
    computed['tagged'] = getattr(syn.tag, 'tagged', None)
    computed['time_tagged'] = getattr(syn.tag, 'time_tagged', None)
    # ConsolidationProteinPool
    computed['pool_available'] = getattr(syn.pool, 'available', None)
    # AMPARecyclingEndosome
    computed['endosome_pool_count'] = getattr(syn.endosome, 'pool_count', None)
    # PostSynapticDensity
    computed['psd_ampa_count'] = getattr(syn.psd, 'ampa_count', None)
    # TraffickingParameters
    computed['insertion_rate'] = getattr(syn.traf_params, 'insertion_rate', None)
    computed['removal_rate'] = getattr(syn.traf_params, 'removal_rate', None)
    # Astrocyte
    computed['astrocyte_monitored_activity'] = getattr(syn.astrocyte, 'monitored_activity', None)
    computed['astrocyte_tnf_alpha'] = getattr(syn.astrocyte, 'tnf_alpha', None)
    computed['astrocyte_d_serine'] = getattr(syn.astrocyte, 'd_serine', None)
    computed['astrocyte_atp'] = getattr(syn.astrocyte, 'atp', None)

    # --- Simple in-memory log/history (for demo only, not persistent) ---
    if not hasattr(plasticity_report, 'history_log'):
        plasticity_report.history_log = []

    # --- Details toggle (for advanced fields) ---
    show_details = request.GET.get('show_details', '0') == '1'


    last_action = None
    if request.method == 'POST':
        action = request.POST.get('action')
        # Special handling for methods that require related objects
        if action == 'nmda_try_open':
            syn.nmda.try_open(syn.cleft, syn.membrane)
            last_action = 'Tried to open NMDA receptor'
        elif action == 'da_try_bind':
            syn.da_receptor.try_bind(syn.da_cleft)
            last_action = 'Tried to bind dopamine receptor'
        else:
            func = ACTIONS_DICT.get(action)
            if func:
                func(request.POST)
                # Make a human-readable label for the action, in the same order as ACTIONS
                action_labels = [
                    ('cleft_release', 'Released glutamate'),
                    ('cleft_clear', 'Cleared glutamate'),
                    ('da_release', 'Released dopamine'),
                    ('da_clear', 'Cleared dopamine'),
                    ('nmda_reset', 'Reset NMDA receptor'),
                    ('da_unbind', 'Unbound dopamine receptor'),
                    ('cascade_activate', 'Activated cascade'),
                    ('membrane_depolarize', 'Depolarized membrane'),
                    ('membrane_reset', 'Reset membrane'),
                    ('spine_influx', 'Ca²⁺ influx'),
                    ('spine_clear_ca', 'Cleared Ca²⁺'),
                    ('spine_modulate_sensitivity', 'Modulated spine sensitivity'),
                    ('tag_set', 'Set synaptic tag'),
                    ('tag_clear', 'Cleared synaptic tag'),
                    ('pool_consume', 'Consumed protein'),
                    ('endosome_remove', 'Removed AMPARs from endosome'),
                    ('endosome_add', 'Added AMPARs to endosome'),
                    ('psd_add', 'Added AMPARs to PSD'),
                    ('psd_remove', 'Removed AMPARs from PSD'),
                    ('trafficking_compute_insertion', 'Computed AMPAR insertion'),
                    ('trafficking_compute_removal', 'Computed AMPAR removal'),
                    ('astrocyte_sense_activity', 'Astrocyte sensed activity'),
                    ('astrocyte_clear_transmitters', 'Astrocyte cleared transmitters'),
                ]
                label_dict = dict(action_labels)
                last_action = label_dict.get(action, f"Action '{action}' performed")
        # --- Add to in-memory log ---
        if last_action:
            from datetime import datetime
            plasticity_report.history_log.append({
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'action': last_action
            })
        # After POST, reload the page with a GET and show the last action
        return redirect(f"{request.path}?last_action={last_action}")

    # Get last_action from query params if present
    from urllib.parse import unquote
    import re
    last_action_param = None
    if 'last_action' in request.GET:
        last_action_param = request.GET.get('last_action')
        # Clean up the string (remove +, %20, etc.)
        if last_action_param:
            last_action_param = unquote(last_action_param)
            last_action_param = re.sub(r'[+]', ' ', last_action_param)

    # --- Pass computed/derived values, log, and details toggle to template ---
    context = {
        'synapse': syn,
        'last_action': last_action_param,
        'computed': computed,
        'history_log': getattr(plasticity_report, 'history_log', []),
        'show_details': show_details,
        'ACTIONS': ACTIONS,
    }
    return render(request, 'synapse/plasticity_report.html', context)
