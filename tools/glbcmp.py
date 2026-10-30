# glbcmp.py A.glb B.glb : compare two glb files by content, per mesh name (order-insensitive), with a float tolerance
import json,struct,sys
import numpy as np
CT={5126:np.float32,5123:np.uint16,5125:np.uint32,5121:np.uint8}
NC={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4,'MAT4':16}
def load(p):
    b=open(p,'rb').read(); n=struct.unpack('<I',b[12:16])[0]
    j=json.loads(b[20:20+n]); rest=b[20+n:]; bl=struct.unpack('<I',rest[:4])[0]
    return j,rest[8:8+bl]
def acc(j,bin_,i):
    a=j['accessors'][i]; bv=j['bufferViews'][a['bufferView']]
    dt=CT[a['componentType']]; nc=NC[a['type']]
    off=bv.get('byteOffset',0)+a.get('byteOffset',0)
    return np.frombuffer(bin_,dtype=dt,count=a['count']*nc,offset=off).reshape(a['count'],nc)
def meshes(j,bin_):
    out={}
    for m in j['meshes']:
        prims=[]
        for p in m['primitives']:
            pos=acc(j,bin_,p['attributes']['POSITION']); idx=acc(j,bin_,p['indices']).ravel() if 'indices' in p else None
            tri=pos[idx].reshape(-1,9) if idx is not None else pos
            mat=j['materials'][p['material']]['name'] if 'material' in p else ''
            # order-insensitive: sort triangles
            t=np.round(tri.astype(np.float64),4); t=t[np.lexsort(t.T[::-1])]
            prims.append((mat,t))
        prims.sort(key=lambda x:(x[0],len(x[1])))
        out.setdefault(m['name'],[]).append(prims)
    return out
ja,ba=load(sys.argv[1]); jb,bb=load(sys.argv[2])
ma,mb=meshes(ja,ba),meshes(jb,bb)
bad=0; worst=0.0
for k in sorted(set(ma)|set(mb)):
    if k not in ma or k not in mb: print('only in one:',k); bad+=1; continue
    for pa,pb in zip(ma[k],mb[k]):
        if len(pa)!=len(pb) or any(x[0]!=y[0] or x[1].shape!=y[1].shape for x,y in zip(pa,pb)):
            bad+=1; print('shape differs:',k,[(x[0],x[1].shape) for x in pa],[(y[0],y[1].shape) for y in pb]); continue
        for x,y in zip(pa,pb):
            d=float(np.abs(x[1]-y[1]).max()) if len(x[1]) else 0.0
            worst=max(worst,d)
            if d>0.002: bad+=1; print('moved:',k,x[0],round(d,4))
na=sorted(n.get('name','') for n in ja['nodes']); nb=sorted(n.get('name','') for n in jb['nodes'])
mats_a=sorted(json.dumps(m,sort_keys=True) for m in ja['materials']); mats_b=sorted(json.dumps(m,sort_keys=True) for m in jb['materials'])
print('meshes',len(ma),len(mb),'nodes same:',na==nb,'materials same:',mats_a==mats_b,'differences:',bad,'largest shift (m):',worst)
# images by name (their bytes), node placement by name (translation/rotation/scale, mesh name), UVs and normals per mesh
import hashlib
def imgs(j,b):
    out=[]
    for im in j.get('images',[]):
        bv=j['bufferViews'][im['bufferView']]; o=bv.get('byteOffset',0)
        out.append((im.get('name',''),hashlib.sha256(b[o:o+bv['byteLength']]).hexdigest()))
    return sorted(out)
def nodes(j):
    out=[]
    for n in j['nodes']:
        m=j['meshes'][n['mesh']]['name'] if 'mesh' in n else ''
        out.append((n.get('name',''),m,tuple(np.round(n.get('translation',[0,0,0]),4)),tuple(np.round(n.get('rotation',[0,0,0,1]),4)),tuple(np.round(n.get('scale',[1,1,1]),4)),len(n.get('children',[]))))
    return sorted(out)
def attrs(j,b,key):
    s=0.0
    for m in j['meshes']:
        for p in m['primitives']:
            if key in p['attributes']:
                a=acc(j,b,p['attributes'][key]).astype(np.float64); s+=float(np.round(a,4).sum())
    return round(s,2)
print('images same:',imgs(ja,ba)==imgs(jb,bb),'placements same:',nodes(ja)==nodes(jb),
      'uv total',attrs(ja,ba,'TEXCOORD_0'),attrs(jb,bb,'TEXCOORD_0'),'normal total',attrs(ja,ba,'NORMAL'),attrs(jb,bb,'NORMAL'))
