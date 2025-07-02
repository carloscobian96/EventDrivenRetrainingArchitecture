from django.shortcuts import render
from .models import Synapse

from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.shortcuts import redirect

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

    # --- Computed/derived values for UI ---
    computed = {}
    # Cleft
    try:
        computed['cleft_is_active'] = getattr(syn.cleft, 'is_active', None)
        computed['cleft_glutamate'] = getattr(syn.cleft, 'glutamate', None)
        computed['cleft_min'] = getattr(syn.cleft, 'min', None)
        computed['cleft_max'] = getattr(syn.cleft, 'max', None)
    except Exception:
        computed['cleft_is_active'] = None
        computed['cleft_glutamate'] = None
        computed['cleft_min'] = None
        computed['cleft_max'] = None
    # Membrane
    try:
        computed['membrane_potential'] = getattr(syn.membrane, 'potential', None)
        computed['membrane_depolarized'] = getattr(syn.membrane, 'is_depolarized', None)
        computed['membrane_min'] = getattr(syn.membrane, 'min', None)
        computed['membrane_max'] = getattr(syn.membrane, 'max', None)
    except Exception:
        computed['membrane_potential'] = None
        computed['membrane_depolarized'] = None
        computed['membrane_min'] = None
        computed['membrane_max'] = None
    # NMDA
    try:
        computed['nmda_open'] = getattr(syn.nmda, 'is_open', None)
        computed['nmda_blocked'] = getattr(syn.nmda, 'is_blocked', None)
        computed['nmda_ca_conductance'] = getattr(syn.nmda, 'ca_conductance', None)
        computed['nmda_min'] = getattr(syn.nmda, 'min', None)
        computed['nmda_max'] = getattr(syn.nmda, 'max', None)
    except Exception:
        computed['nmda_open'] = None
        computed['nmda_blocked'] = None
        computed['nmda_ca_conductance'] = None
        computed['nmda_min'] = None
        computed['nmda_max'] = None
    # Spine
    try:
        computed['spine_ca'] = getattr(syn.spine, 'ca', None)
        computed['spine_elevated'] = getattr(syn.spine, 'is_elevated', None)
        computed['spine_min'] = getattr(syn.spine, 'min', None)
        computed['spine_max'] = getattr(syn.spine, 'max', None)
    except Exception:
        computed['spine_ca'] = None
        computed['spine_elevated'] = None
        computed['spine_min'] = None
        computed['spine_max'] = None
    # DA Cleft
    try:
        computed['da_cleft_level'] = getattr(syn.da_cleft, 'level', None)
        computed['da_cleft_high'] = getattr(syn.da_cleft, 'is_high', None)
        computed['da_cleft_min'] = getattr(syn.da_cleft, 'min', None)
        computed['da_cleft_max'] = getattr(syn.da_cleft, 'max', None)
    except Exception:
        computed['da_cleft_level'] = None
        computed['da_cleft_high'] = None
        computed['da_cleft_min'] = None
        computed['da_cleft_max'] = None
    # DA Receptor
    try:
        computed['da_receptor_bound'] = getattr(syn.da_receptor, 'is_bound', None)
        computed['da_receptor_active'] = getattr(syn.da_receptor, 'is_active', None)
        computed['da_receptor_affinity'] = getattr(syn.da_receptor, 'affinity', None)
    except Exception:
        computed['da_receptor_bound'] = None
        computed['da_receptor_active'] = None
        computed['da_receptor_affinity'] = None
    # Cascade
    try:
        computed['cascade_active'] = getattr(syn.cascade, 'is_active', None)
    except Exception:
        computed['cascade_active'] = None
    # Tag
    try:
        computed['tagged'] = getattr(syn.tag, 'is_tagged', None)
    except Exception:
        computed['tagged'] = None
    # Pool
    try:
        computed['pool_size'] = getattr(syn.pool, 'size', None)
        computed['pool_min'] = getattr(syn.pool, 'min', None)
        computed['pool_max'] = getattr(syn.pool, 'max', None)
    except Exception:
        computed['pool_size'] = None
        computed['pool_min'] = None
        computed['pool_max'] = None
    # Endosome
    try:
        computed['endosome_count'] = getattr(syn.endosome, 'count', None)
        computed['endosome_min'] = getattr(syn.endosome, 'min', None)
        computed['endosome_max'] = getattr(syn.endosome, 'max', None)
    except Exception:
        computed['endosome_count'] = None
        computed['endosome_min'] = None
        computed['endosome_max'] = None
    # PSD
    try:
        computed['psd_count'] = getattr(syn.psd, 'count', None)
        computed['psd_min'] = getattr(syn.psd, 'min', None)
        computed['psd_max'] = getattr(syn.psd, 'max', None)
    except Exception:
        computed['psd_count'] = None
        computed['psd_min'] = None
        computed['psd_max'] = None
    # Trafficking
    try:
        computed['trafficking_insertion'] = getattr(syn.traffickingparams, 'insertion', None)
        computed['trafficking_removal'] = getattr(syn.traffickingparams, 'removal', None)
        computed['trafficking_turnover_rate'] = getattr(syn.traffickingparams, 'turnover_rate', None)
    except Exception:
        computed['trafficking_insertion'] = None
        computed['trafficking_removal'] = None
        computed['trafficking_turnover_rate'] = None
    # Astrocyte
    try:
        computed['astrocyte_activity'] = getattr(syn.astrocyte, 'activity', None)
        computed['astrocyte_min'] = getattr(syn.astrocyte, 'min', None)
        computed['astrocyte_max'] = getattr(syn.astrocyte, 'max', None)
    except Exception:
        computed['astrocyte_activity'] = None
        computed['astrocyte_min'] = None
        computed['astrocyte_max'] = None
    # Add more as needed for your models

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
