import nibabel
import matplotlib.pyplot as plt
import numpy as np
import scipy.signal

epifile='/home/mkayvanrad/data/healthyvolunteer/nii/7130/20140312/restingboldshortTRmpmotor.nii.gz'
TR=0.380;


img_nib=nibabel.load(epifile)
img=img_nib.get_data()

img.shape

s=img[32,32,4,:]
# s=np.array(s,dtype=float)
plt.figure(1)
plt.hold(False)
plt.plot(s, linewidth=1.0)
plt.title('Original signal')

plt.savefig('/home/mkayvanrad/scratch/test_pyplot.png',dpi=600)

S=np.fft.fft(s)

l=len(S)
fs=1/TR
f=fs*np.arange(0,int(l/2))/l

plt.figure(2)
plt.hold(False)
plt.plot(f,2*np.abs(S[0:int(l/2)])/l)
#plt.ylim(0,1)
plt.title('Original Fourier')

## filter design

# butterworth lowpass
Fstop=0.1/(fs/2)

(b,a)=scipy.signal.butter(5,Fstop,btype='lowpass')

(w,h)=scipy.signal.freqz(b,a)
plt.figure(3)
plt.hold(False)
plt.plot(w/np.pi,20*np.log10(abs(h)))

sfilt = scipy.signal.lfilter(b,a,s)
plt.figure(1)
plt.hold(True)
plt.plot(sfilt)
Sfilt=np.fft.fft(sfilt)
plt.figure(2)
plt.hold(True)
plt.plot(f,2*np.abs(Sfilt[0:int(l/2)])/l)
#plt.ylim(0,1)

sfilt = scipy.signal.filtfilt(b,a,s)
plt.figure(1)
plt.hold(True)
plt.plot(sfilt)
Sfilt=np.fft.fft(sfilt)
plt.figure(2)
plt.hold(True)
plt.plot(f,2*np.abs(Sfilt[0:int(l/2)])/l)
#plt.ylim(0,1)

imgfilt = scipy.signal.lfilter(b,a,img,axis=-1)
s_imgfilt=imgfilt[32,32,4,:]
plt.figure(1)
plt.hold(True)
plt.plot(s_imgfilt)



# butterworth highpass
Fstop=0.1/(fs/2)

(b,a)=scipy.signal.butter(5,Fstop,btype='highpass')

(w,h)=scipy.signal.freqz(b,a)
plt.figure(3)
plt.hold(True)
plt.plot(w/np.pi,20*np.log10(abs(h)))

sfilt = scipy.signal.lfilter(b,a,s)
plt.figure(1)
plt.hold(True)
plt.plot(sfilt)

Sfilt=np.fft.fft(sfilt)
plt.figure(2)
plt.hold(True)
plt.plot(f,2*np.abs(Sfilt[0:int(l/2)])/l)
#plt.ylim(0,1)

# butterworth bandpass
Fstop1=0.1/(fs/2)
Fstop2=0.5/(fs/2)

(b,a)=scipy.signal.butter(5,(Fstop1,Fstop2),btype='bandpass')

(w,h)=scipy.signal.freqz(b,a)
plt.figure(3)
plt.hold(True)
plt.plot(w/np.pi,20*np.log10(abs(h)))

# FIR (window method)
b = scipy.signal.firwin(20,Fstop1,pass_zero=True)

(w,h)=scipy.signal.freqz(b)
plt.figure(3)
plt.hold(True)
plt.plot(w/np.pi,20*np.log10(abs(h)))

# filter the signal
sfilt = scipy.signal.lfilter(b,1,s)

plt.figure(1)
plt.hold(True)
plt.plot(sfilt)

Sfilt=np.fft.fft(sfilt)
plt.figure(2)
plt.hold(True)
plt.plot(f,2*np.abs(Sfilt[0:int(l/2)])/l)
#plt.ylim(0,1)





# 