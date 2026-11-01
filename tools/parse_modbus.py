import re,sys
def crc(d):
    c=0xFFFF
    for b in d:
        c^=b
        for _ in range(8): c=(c>>1)^0xA001 if c&1 else c>>1
    return c
data=[]
for l in open(sys.argv[1]):
    m=re.search(r'<<< (.*)',l)
    if m: data+= [int(x,16) for x in m.group(1).split()]
# greedy frame split by CRC
i=0;frames=[]
while i<len(data):
    for L in range(4,40):
        f=data[i:i+L]
        if len(f)==L and crc(f[:-2])==(f[-2]|f[-1]<<8):
            frames.append(f);i+=L;break
    else: i+=1
ok=0;pend=None;res={}
for f in frames:
    fc=f[1]
    if fc in(1,3) and len(f)==8: pend=f;continue
    if fc==5: print('WRITE COIL',hex(f[2]<<8|f[3]),'=',hex(f[4]<<8|f[5]));continue
    if pend and fc==pend[1]:
        a=pend[2]<<8|pend[3];n=pend[4]<<8|pend[5];p=f[3:-2]
        if fc==3: vals=[p[k]<<8|p[k+1] for k in range(0,len(p),2)]
        else: vals=[bin(p[0])]
        res.setdefault((fc,a,n),[]).append(tuple(vals))
        pend=None
for k,v in sorted(res.items()):
    s=sorted(set(v))
    print('FC%d addr %d (0x%X) n=%d:'%(k[0],k[1],k[1],k[2]), s[:4])
print(len(frames),'frames')
