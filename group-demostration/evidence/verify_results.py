"""Recompute only the finite numerical assertions used in the presentation.

Run from any directory: python3 path/to/group-demostration/evidence/verify_results.py
No Vizard, OpenSim, MATLAB, or third-party Python package is required.
This checks exported data and the script's geometric calculation, not GUI playback.
"""
from pathlib import Path
import ast
import contextlib
import csv
import datetime
import hashlib
import io
import json
import math
import platform
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
FILES = [
    'src/script/topspin_affordance_scene.py',
    'src/motion-data/Top_spin_SegmentPosition.csv',
    'src/motion-data/Top_spin_SegmentOrientation.csv',
    'src/required-assets/elbow_flex_l.csv',
    'src/required-assets/left_hand_height.csv',
    'src/required-assets/Top_spin-001_Xsens_jointangle_q.mot',
    'src/required-assets/info_theory.m',
    'group-report/annexes/anexo_b_teoria_informacion.tex',
    'group-demostration/evidence/verify_results.py',
]
def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()
def vector(a,b):
    return [x-y for x,y in zip(a,b)]
def norm(a):
    return math.sqrt(sum(x*x for x in a))
def numeric_rows(p):
    return [[float(v) for v in line.split()] for line in p.read_text().splitlines()[1:] if line.strip()]
def write_csv(name,fields,rows):
    with (HERE/name).open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)

def entropy(probabilities):
    return -sum(p*math.log2(p) for p in probabilities if p>0)

def mutual_information(counts):
    total=sum(map(sum,counts))
    rowsums=[sum(r) for r in counts]
    colsums=[sum(r[j] for r in counts) for j in range(len(counts[0]))]
    return sum(x/total*math.log2(x*total/(rowsums[i]*colsums[j]))
               for i,row in enumerate(counts) for j,x in enumerate(row) if x>0)

def information_analysis(ns):
    speeds=ns['speeds'];path=ns['proxy_path'];n=len(path)
    available=speeds[:];peaks=[]
    for _ in range(3):
        i=max(range(n),key=lambda j:available[j]);peaks.append(i)
        for j in range(max(0,i-30),min(n,i+31)):available[j]=0
    peaks.sort()
    assert peaks==[101,185,260]
    windows=[list(range(i-15,i+16)) for i in peaks]
    assert all(len(w)==31 for w in windows)
    assert min(speeds)>=0 and max(speeds)<8
    bins=[]
    for indices in [list(range(n))]+windows:
        counts=[0]*8
        for i in indices:counts[min(7,int(speeds[i]))]+=1
        bins.append(counts)
    ent=[entropy([x/sum(c) for x in c]) for c in bins]
    probs=[[(x+.5)/35 for x in c] for c in bins[1:]]
    kl=[[sum(p*math.log2(p/q) for p,q in zip(a,b)) for b in probs] for a in probs]
    mins=[[min(norm(vector(path[i],ball)) for i in win) for win in windows] for ball in ns['balls']]
    successes=[sum(d<=.095 for d in row) for row in mins]
    assert successes==[3,1,0,0]
    near_far=[[sum(successes[:2]),6-sum(successes[:2])],
              [sum(successes[2:]),6-sum(successes[2:])]]
    mi=mutual_information(near_far)
    h=entropy([4/12,8/12]);conditional=.5*entropy([4/6,2/6])
    assert abs(mi-(h-conditional))<1e-12
    mean=[sum(path[i][axis] for i in peaks)/3 for axis in range(3)]
    spread=math.sqrt(sum(norm(vector(path[i],mean))**2 for i in peaks)/3)
    frame_events=[]
    for ball in ns['balls']:
        counts=[[0,0],[0,0]]
        for i,p in enumerate(path):
            counts[0 if speeds[i]>=4 else 1][0 if norm(vector(p,ball))<=.095 else 1]+=1
        frame_events.append(dict(counts=counts,mutual_information_bits=mutual_information(counts)))
    observer=[[.425,.075],[.1,.4]]
    prediction_changes=[]
    for j,s in enumerate(successes):
        q=(int(mins[j][1]<=.095)+1)/3;p=(s+1)/5
        divergence=p*math.log2(p/q)+(1-p)*math.log2((1-p)/(1-q))
        prediction_changes.append(dict(reference_only=q,three_strokes=p,kl_bits=divergence))
    write_csv('speed-series.csv',['time_s','proxy_speed_m_s'],
              [dict(time_s=i/60,proxy_speed_m_s=v) for i,v in enumerate(speeds)])
    write_csv('speed-occupancy.csv',['bin_centre','whole','s1','s2','s3'],
              [dict(bin_centre=j+.5,whole=bins[0][j]/n,s1=bins[1][j]/31,
                    s2=bins[2][j]/31,s3=bins[3][j]/31) for j in range(8)])
    return dict(peak_frames=peaks,peak_times_s=[i/60 for i in peaks],
                peak_speeds_m_s=[speeds[i] for i in peaks],rms_peak_position_spread_m=spread,
                speed_bin_counts=bins,entropy_bits=ent,entropy_nats=[x*math.log(2) for x in ent],
                smoothed_kl_bits=kl,condition_by_stroke_min_distance_m=mins,
                intercepts_per_three_windows=successes,near_far_counts=near_far,
                outcome_entropy_bits=h,near_far_mutual_information_bits=mi,
                condition_mutual_information_bits=mutual_information([[s,3-s] for s in successes]),
                frame_events=frame_events,predictive_changes=prediction_changes,
                illustrative_observer=dict(assumed_prior=.5,assumed_hit_rate=.85,assumed_false_alarm_rate=.2,
                                          p_feasible_given_yes=.425/.525,p_feasible_given_no=.075/.475,
                                          mutual_information_bits=mutual_information(observer)),
                limits=['One recorded trial, three dependent selected windows',
                        'Histogram occupancy discards temporal order and depends on bins',
                        'No valid iid entropy-bias correction claimed for autocorrelated frames',
                        'Beta predictions require an illustrative exchangeability assumption',
                        'Observer hit/false-alarm rates are assumed, not observed'])

def main():
    started=datetime.datetime.now(datetime.timezone.utc).isoformat()
    clock=time.perf_counter()
    before={p:digest(ROOT/p) for p in FILES}
    script=ROOT/FILES[0]
    # Execute the reviewed data/calculation prefix only. Remove engine imports.
    # Functions referring to viz are defined but never called.
    source=script.read_text().split('# ============================================================\n# SCENE')[0]
    tree=ast.parse(source)
    tree.body=[n for n in tree.body if not (isinstance(n,ast.Import) and any(a.name in {'viz','vizact','vizshape'} for a in n.names))]
    ns={'__file__':str(script)}
    with contextlib.redirect_stdout(io.StringIO()):
        exec(compile(tree,str(script),'exec'),ns)

    # Independent reconstruction in the original right-handed Xsens coordinates.
    with (ROOT/FILES[1]).open() as f:
        rows=list(csv.DictReader(f))
    def point(row,name):return [float(row[name+' '+axis]) for axis in ['x','y','z']]
    path=[]
    for row in rows:
        hand=point(row,'Left Hand');forearm=point(row,'Left Forearm')
        direction=vector(hand,forearm);length=norm(direction)
        path.append([a+0.1*b/length for a,b in zip(hand,direction)])
    peak=max(range(1,len(path)),key=lambda i:norm(vector(path[i],path[i-1])))
    assert peak==ns['i_ref']==185
    outward=vector(path[peak],point(rows[peak],'Pelvis'));outward[2]=0
    length=norm(outward);outward=[x/length for x in outward]
    conditions=[]
    for index,d in enumerate(ns['CONDITIONS']):
        target=[a+d*b for a,b in zip(path[peak],outward)]
        distances=[norm(vector(p,target)) for p in path]
        i=min(range(len(distances)),key=lambda j:distances[j])
        nearest=distances[i]
        assert abs(nearest-ns['results'][index][0])<1e-12
        assert i==ns['results'][index][1]
        conditions.append(dict(condition=f'C{index+1}',offset_m=d,min_distance_m=nearest,closest_frame=i,
                               closest_time_s=i/60,margin_m=.095-nearest,intercept=nearest<=.095))
    e=numeric_rows(ROOT/FILES[3]);h=numeric_rows(ROOT/FILES[4])
    assert len(e)==len(h)==len(rows)==ns['nframes']==379
    mot=(ROOT/FILES[5]).read_text().split('endheader',1)[1].strip().splitlines()
    keys=mot[0].split();motrows=[[float(x) for x in r.split()] for r in mot[1:] if r.strip()]
    elbowcol=keys.index('elbow_flex_l')
    checks=[]
    for i in [150,185,216]:
        assert abs(motrows[i][elbowcol]-e[i][2])<1e-9
        assert abs(e[i][1]-i/60)<=.0011
        assert abs(h[i][0]-i/60)<=.0011
        v_elbow=ns['elbow_flexion'](i);v_height=ns['positions'][i]['Left Hand'][1]
        checks.append(dict(frame=i,vizard_time_s=i/60,opensim_time_s=h[i][0],
                           opensim_elbow_deg=e[i][2],vizard_elbow_deg=v_elbow,
                           delta_elbow_deg=v_elbow-e[i][2],opensim_height_m=h[i][2],
                           vizard_height_m=v_height,delta_height_m=v_height-h[i][2]))
    write_csv('conditions.csv',list(conditions[0]),conditions)
    write_csv('validation.csv',list(checks[0]),checks)
    series=[dict(time_s=i/60,opensim_time_s=h[i][0],opensim_height_m=h[i][2],
                 vizard_height_m=ns['positions'][i]['Left Hand'][1],
                 opensim_elbow_deg=e[i][2],vizard_elbow_deg=ns['elbow_flexion'](i)) for i in range(len(rows))]
    write_csv('kinematics.csv',list(series[0]),series)
    result={'source_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
            'frame_count':len(rows),'sampling_hz':60,'duration_s':378/60,
            'reference_frame':peak,'reference_time_s':peak/60,'peak_proxy_speed_m_s':ns['speeds'][peak],
            'conditions':conditions,'validation':checks,'annex_b':information_analysis(ns),
            'assertion_tested':'Four full-trial discrete proxy distances, three matched-row export comparisons, and Annex B entropy, KL, mutual information and illustrative Bayesian calculations.',
            'non_claims':['No Vizard GUI execution','No OpenSim rerun or synchronized OpenSim pose capture',
                          'No measured racket-ball impact','No participant judgments','No maximum actor capability']}
    (HERE/'results.json').write_text(json.dumps(result,indent=2)+'\n')
    after={p:digest(ROOT/p) for p in FILES}
    assert before==after
    outputs=['conditions.csv','validation.csv','kinematics.csv','speed-series.csv','speed-occupancy.csv','results.json']
    manifest={
        'schema_version':2,'claim_id':'presentation-export-checks',
        'repository':{'commit':result['source_commit'],'dirty':bool(subprocess.check_output(['git','status','--porcelain'],cwd=ROOT,text=True))},
        'command':[sys.executable,str(Path(__file__).resolve())],
        'environment':{'software':[{'name':'Python','version':platform.python_version()}],'hardware':platform.platform()+' '+platform.machine()},
        'mathematics':{'assertion_tested':result['assertion_tested'],'coefficient_domain':'IEEE-754 binary64',
                       'conventions':'Zero-based rows; 60 Hz; positions in metres; elbow flexion in degrees; delta = Vizard - OpenSim.',
                       'inputs':FILES,'bounds':{'frames':379,'conditions':4,'validation_frames':[150,185,216],
                                               'distance_tolerance_m':1e-12,'stroke_windows':3,'frames_per_window':31,'speed_bins':8},
                       'non_claims':result['non_claims']},
        'randomness':{'used':False,'generator':'','seed':None},
        'run':{'started_at':started,'runtime_seconds':time.perf_counter()-clock,'exit_status':0,'status':'completed',
               'resource_limits':{'memory_bytes':None,'cpu_seconds':None,'max_cores':1,'max_threads':1}},
        'outputs':[{'path':str((HERE/p).relative_to(ROOT)),'sha256':digest(HERE/p),'kind':'result'} for p in outputs],
        'checks':['Independent Xsens-coordinate distance reconstruction agrees to 1e-12 m.',
                  '379 rows in each export; three sampled times differ by at most 1.1 ms.',
                  'Three elbow CSV values agree with the original .mot file.',
                  'Annex B peak selection and success counts reproduced; mutual-information identity cross-checked.',
                  'Before/after hashes identical for every input.'],
        'result':'Finite assertions verified in the stated range, conditional on supplied export conventions.',
        'residual_risks':['Export metadata contains a duplicate time header and misleading inDegrees=no for elbow values.',
                          'Matching rows assume the supplied files represent the same trial; source acquisition not independently verified.',
                          'Discrete sample intersections do not establish continuous collision or successful return.',
                          'Cross-pipeline discrepancies do not define a calibrated spatial error bound.'],
        'input_artifacts':[{'path':p,'sha256':before[p],'sha256_after':after[p]} for p in FILES],
        'declared_results':[str((HERE/p).relative_to(ROOT)) for p in outputs]}
    (HERE/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps(result,indent=2))
if __name__=='__main__':main()
