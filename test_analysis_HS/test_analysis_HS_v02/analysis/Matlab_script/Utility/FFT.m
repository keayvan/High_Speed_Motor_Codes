%--------------------------------------------------------------------------
%-----------------------   Fourier trasformation   ------------------------
%--------------------------------------------------------------------------

function [Fourier2,Angles,OUT] = FFT(IN,H)

punti = length(IN) ;
F = 50 ;

n = length(IN);
% time = (1/(F*(punti-1)):1/(F*(punti-1)):1/F);
time = linspace(1/F/punti,1/F,punti);

Fourier1 = fft(IN)/n*2;
Fourier2 = abs(Fourier1(2:round(n/2))) ;
Angles   = angle(Fourier1(2:round(n/2))) ;

for i = 1 : length(H) %punti/2 ;
    for j = 1 : length(time) 
        OUT(j,i) = Fourier2(H(i))*cos(H(i)*2*pi*F*time(j)+Angles(H(i))) ;
    end
end
OUT=sum(OUT,2);
% Remove zero rows
OUT( all(~OUT,2), : ) = [];
% Remove zero columns
OUT( :, all(~OUT,1) ) = [];