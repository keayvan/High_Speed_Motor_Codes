clear all; close all; clc

addpath Utility

%----
% Name = 'ARC_P43_32192_3phases_frequency_60KHz_steps\analog.csv';
% Path = 'D:\ARQUIMEA GROUP\Keayvan Keramati - phaseAnalysis\data\raw\Salea\' ;
% uiopen(fullfile(Path,Name),1)

% Name = 'ARC_P43_32193_3phases_selection_steps_fullRes.csv';
% Path = 'D:\ARQUIMEA GROUP\Keayvan Keramati - phaseAnalysis\data\raw\TYTO\' ;
% uiopen(fullfile(Path,Name),1)

% load('P43_32193.mat')
% P43(1).Name='P43-32193';
% P43(1).Salea=Salea; clear Salea
% P43(1).Tyto=Tyto; clear Tyto

%----
% Name = 'ARC_P43_32192_3phases_frequency60KHz_steps_fullRes.csv';
% Path = 'C:\Users\amarfoli\ARQUIMEA GROUP\Keayvan Keramati - phaseAnalysis\data\raw\TYTO\' ;
% % Path = 'D:\ARQUIMEA GROUP\Keayvan Keramati - phaseAnalysis\data\raw\TYTO\' ;
% uiopen(fullfile(Path,Name),1)

% Name = 'ARC_P43_32192_selection_steps_01_fullRes.csv';
% Path = 'D:\ARQUIMEA GROUP\Keayvan Keramati - phaseAnalysis\data\raw\TYTO\' ;
% uiopen(fullfile(Path,Name),1)

load('P43_32193_01.mat')
P43_32193(1).Name='P43-32193-01';
P43_32193(1).Tyto=Tyto; clear Tyto
P43_32193(1).Salea=[]; 
load('P43_32193_01.mat')
P43_32193(2).Name='P43-32193-02';
P43_32193(2).Tyto=Tyto; clear Tyto
P43_32193(2).Salea=[]; 
load('P43_32193_03.mat')
P43_32193(3).Name='P43-32193-03';
P43_32193(3).Tyto=Tyto; clear Tyto
P43_32193(3).Salea=[]; 
load('P43_32193_04.mat')
P43_32193(4).Name='P43-32193-04';
P43_32193(4).Tyto=Tyto; clear Tyto
P43_32193(4).Salea=[]; 
load('P43_32193_05.mat')
P43_32193(5).Name='P43-32193-05';
P43_32193(5).Tyto=Tyto; clear Tyto
P43_32193(5).Salea=[]; 
load('P43_32193_06.mat')
P43_32193(6).Name='P43-32193-06';
P43_32193(6).Tyto=Tyto; clear Tyto
P43_32193(6).Salea=[]; 
load('P43_32193_07.mat')
P43_32193(7).Name='P43-32193-07';
P43_32193(7).Tyto=Tyto; clear Tyto
P43_32193(7).Salea=[]; 
load('P43_32193_08.mat')
P43_32193(8).Name='P43-32193-08';
P43_32193(8).Tyto=Tyto; clear Tyto
P43_32193(8).Salea=[]; 
load('P43_32193_09.mat')
P43_32193(9).Name='P43-32193-09';
P43_32193(9).Tyto=Tyto; clear Tyto
P43_32193(9).Salea=[]; 


load('P43_32192_01.mat')
P43_32192(1).Name='P43-32192-01';
P43_32192(1).Tyto=Tyto; clear Tyto
P43_32193(1).Salea=[]; 

load('P43_32192_40KHz.mat')
P43_32192(2).Name='P43-32192-40KHz';
P43_32192(2).Tyto=Tyto; clear Tyto
P43_32192(2).Salea=Salea; clear Salea

load('P43_32192_20KHz.mat')
P43_32192(3).Name='P43-32192-20KHz';
P43_32192(3).Tyto=Tyto; clear Tyto
P43_32192(3).Salea=Salea; clear Salea

load('P43_32192_60KHz.mat')
P43_32192(4).Name='P43-32192-60KHz';
P43_32192(4).Tyto=Tyto; clear Tyto
P43_32192(4).Salea=Salea; clear Salea

Flag_salea=1;



%%
%--- Tyto results
close all;clc

FontS=11;

polepairs=4;

dS=0.5;

DnT = [0.8 1;1.3 1.5;1.8 2;2.3 2.5;2.8 3]*10^4 ;
DnS = [0.1 0.1+dS;1 1+dS;1.9 1.9+dS;2.9 2.9+dS;4 4+dS]*10^3 ;

for qq=1:size(P43_32193,2)

    P43_32193(qq).Torque_tyto = P43_32193(qq).Tyto(:,4) ;
    P43_32193(qq).Torque_tyto = P43_32193(qq).Torque_tyto(~isnan(P43_32193(qq).Tyto(:,4)));
    P43_32193(qq).Time_Torque_tyto = P43_32193(qq).Tyto(:,1) ;
    P43_32193(qq).Time_Torque_tyto = P43_32193(qq).Time_Torque_tyto(~isnan(P43_32193(qq).Tyto(:,4)));
    P43_32193(qq).Speed_tyto = P43_32193(qq).Tyto(:,7) ;
    P43_32193(qq).Speed_tyto = P43_32193(qq).Speed_tyto(~isnan(P43_32193(qq).Tyto(:,7)));

    P43_32193(qq).Idc_tyto = P43_32193(qq).Tyto(:,6) ;
    P43_32193(qq).Vdc_tyto = P43_32193(qq).Tyto(:,5) ;
    P43_32193(qq).Pdc_tyto = P43_32193(qq).Vdc_tyto.*P43_32193(qq).Idc_tyto ;
    P43_32193(qq).Idc_tyto = P43_32193(qq).Idc_tyto(~isnan(P43_32193(qq).Tyto(:,6)));
    P43_32193(qq).Vdc_tyto = P43_32193(qq).Vdc_tyto(~isnan(P43_32193(qq).Tyto(:,5)));
    P43_32193(qq).Pdc_tyto = P43_32193(qq).Pdc_tyto(~isnan(P43_32193(qq).Pdc_tyto));

    for i=1:length(DnT)
    P43_32193(qq).Torque_mean(i)   = mean(P43_32193(qq).Torque_tyto(DnT(i,1):DnT(i,2))) ;
    P43_32193(qq).Speed_mean(i)    = mean(P43_32193(qq).Speed_tyto(DnS(i,1):DnS(i,2))) ;
    P43_32193(qq).Idc_mean_tyto(i) = mean(P43_32193(qq).Idc_tyto(DnT(i,1):DnT(i,2))) ;
    P43_32193(qq).Vdc_mean_tyto(i) = mean(P43_32193(qq).Vdc_tyto(DnT(i,1):DnT(i,2))) ;
    P43_32193(qq).Power_Mech(i)    = P43_32193(qq).Torque_mean(i)*P43_32193(qq).Speed_mean(i)*2*pi/60 ;
    P43_32193(qq).Pdc_mean_tyto(i) = P43_32193(qq).Idc_mean_tyto(i)*P43_32193(qq).Vdc_mean_tyto(i) ;
    end 

    P43_32193(qq).Freq = P43_32193(qq).Speed_mean*polepairs/60 ;
    P43_32193(qq).Period = 1./P43_32193(qq).Freq ;
    P43_32193(qq).Eff_drive_tyto = (P43_32193(qq).Power_Mech./P43_32193(qq).Pdc_mean_tyto)*100 ;

end

for qq=1:size(P43_32193,2)

P43_32193_eff(:,qq) = P43_32193(qq).Eff_drive_tyto ;
P43_32193_speed(:,qq) = P43_32193(qq).Speed_mean/1000 ;

end


for qq=1:size(P43_32192,2)

    P43_32192(qq).Torque_tyto = P43_32192(qq).Tyto(:,4) ;
    P43_32192(qq).Torque_tyto = P43_32192(qq).Torque_tyto(~isnan(P43_32192(qq).Tyto(:,4)));
    P43_32192(qq).Time_Torque_tyto = P43_32192(qq).Tyto(:,1) ;
    P43_32192(qq).Time_Torque_tyto = P43_32192(qq).Time_Torque_tyto(~isnan(P43_32192(qq).Tyto(:,4)));
    P43_32192(qq).Speed_tyto = P43_32192(qq).Tyto(:,7) ;
    P43_32192(qq).Speed_tyto = P43_32192(qq).Speed_tyto(~isnan(P43_32192(qq).Tyto(:,7)));

    P43_32192(qq).Idc_tyto = P43_32192(qq).Tyto(:,6) ;
    P43_32192(qq).Vdc_tyto = P43_32192(qq).Tyto(:,5) ;
    P43_32192(qq).Pdc_tyto = P43_32192(qq).Vdc_tyto.*P43_32192(qq).Idc_tyto ;
    P43_32192(qq).Idc_tyto = P43_32192(qq).Idc_tyto(~isnan(P43_32192(qq).Tyto(:,6)));
    P43_32192(qq).Vdc_tyto = P43_32192(qq).Vdc_tyto(~isnan(P43_32192(qq).Tyto(:,5)));
    P43_32192(qq).Pdc_tyto = P43_32192(qq).Pdc_tyto(~isnan(P43_32192(qq).Pdc_tyto));

    for i=1:length(DnT)
    P43_32192(qq).Torque_mean(i)   = mean(P43_32192(qq).Torque_tyto(DnT(i,1):DnT(i,2))) ;
    P43_32192(qq).Speed_mean(i)    = mean(P43_32192(qq).Speed_tyto(DnS(i,1):DnS(i,2))) ;
    P43_32192(qq).Idc_mean_tyto(i) = mean(P43_32192(qq).Idc_tyto(DnT(i,1):DnT(i,2))) ;
    P43_32192(qq).Vdc_mean_tyto(i) = mean(P43_32192(qq).Vdc_tyto(DnT(i,1):DnT(i,2))) ;
    P43_32192(qq).Power_Mech(i)    = P43_32192(qq).Torque_mean(i)*P43_32192(qq).Speed_mean(i)*2*pi/60 ;
    P43_32192(qq).Pdc_mean_tyto(i) = P43_32192(qq).Idc_mean_tyto(i)*P43_32192(qq).Vdc_mean_tyto(i) ;
    end 

    P43_32192(qq).Freq = P43_32192(qq).Speed_mean*polepairs/60 ;
    P43_32192(qq).Period = 1./P43_32192(qq).Freq ;
    P43_32192(qq).Eff_drive_tyto = (P43_32192(qq).Power_Mech./P43_32192(qq).Pdc_mean_tyto)*100 ;

end

for qq=1:size(P43_32192,2)

P43_32192_eff(:,qq) = P43_32192(qq).Eff_drive_tyto ;
P43_32192_speed(:,qq) = P43_32192(qq).Speed_mean/1000 ;

end




for qq=1:size(P43_32193,2)

figure
subplot(2,2,1);hold on
plot(P43_32193(qq).Torque_tyto)
for i=1:length(DnT)
plot([DnT(i,1) DnT(i,1)],[-1 1],'k')
plot([DnT(i,2) DnT(i,2)],[-1 1],'k')
end
ylabel('Torque [Nm]');xlabel('Samples')
set(gca,'FontName','Times New Roman','fontsize',FontS)
grid
subplot(2,2,2);hold on
plot(P43_32193(qq).Speed_tyto)
for i=1:length(DnT)
plot([DnS(i,1) DnS(i,1)],[-1 15000],'k')
plot([DnS(i,2) DnS(i,2)],[-1 15000],'k')
end
ylabel('Speed [rpm]');xlabel('Samples')
set(gca,'FontName','Times New Roman','fontsize',FontS)
grid
subplot(2,2,3);hold on
plot(P43_32193(qq).Idc_tyto)
for i=1:length(DnT)
plot([DnT(i,1) DnT(i,1)],[-1 100],'k')
plot([DnT(i,2) DnT(i,2)],[-1 100],'k')
end
ylabel('Idc [A]');xlabel('Samples')
set(gca,'FontName','Times New Roman','fontsize',FontS)
grid
subplot(2,2,4);hold on
plot(P43_32193(qq).Pdc_tyto)
for i=1:length(DnT)
plot([DnT(i,1) DnT(i,1)],[-1 2000],'k')
plot([DnT(i,2) DnT(i,2)],[-1 2000],'k')
end
ylabel('Pdc [W]');xlabel('Samples')
set(gca,'FontName','Times New Roman','fontsize',FontS)
grid

sgtitle('Tyto measurements','FontName','Times New Roman','fontsize',FontS+2)

end


figure
for i=1:size(P43_32193,2)
subplot(3,4,i)
bar(P43_32193(i).Speed_mean/1000,P43_32193(i).Eff_drive_tyto)
xticks(round(P43_32193(i).Speed_mean)/1000)
set(gca,'FontName','Times New Roman','fontsize',10)
ylabel('Eff [%]')
xlabel('Speed [krpm]')
ylim([30 100])
grid
t=title(P43_32193(i).Name);
set(t,'Units','normalized')
set(t, 'Position', [0.2 1.05 0])
% h=legend('Power train tyto','FontName','Times New Roman','fontsize',10,'Orientation','horizontal');
% set(h, 'Units','normalized', 'Position',[0.5 0.94 0.1 0.05]);
end


figure
subplot(1,1,1)
hold on
for i=1:size(P43_32193,2)
[h]=plot(P43_32193_speed(:,i),P43_32193_eff(:,i),'o');
h.Annotation.LegendInformation.IconDisplayStyle = 'off';
end
plot(mean(P43_32193_speed,2),mean(P43_32193_eff,2),'sk','MarkerFaceColor','b','MarkerSize',8)
for i=1:2
[h]=plot(P43_32192_speed(:,i),P43_32192_eff(:,i),'v');
h.Annotation.LegendInformation.IconDisplayStyle = 'off';
end
plot(mean(P43_32192_speed(:,1:2),2),mean(P43_32192_eff(:,1:2),2),'sk','MarkerFaceColor','r','MarkerSize',8)
% plot(P43_32192_speed(:,3),P43_32192_eff(:,3),'sk','MarkerFaceColor','m','MarkerSize',8)
% plot(P43_32192_speed(:,4),P43_32192_eff(:,4),'sk','MarkerFaceColor','g','MarkerSize',8)

xlabel('Speed [krpm]')
ylabel('Efficiency [%]')
set(gca,'FontName','Times New Roman','fontsize',12)
legend('P43-32193-sf40kHz','P43-32192-sf40kHz','FontName','Times New Roman','fontsize',16)
grid


figure
hold on
plot(mean(P43_32192_speed(:,1:2),2),mean(P43_32192_eff(:,1:2),2),'sk','MarkerFaceColor','r','MarkerSize',8)
plot(P43_32192_speed(:,3),P43_32192_eff(:,3),'sk','MarkerFaceColor','m','MarkerSize',8)
plot(P43_32192_speed(:,4),P43_32192_eff(:,4),'sk','MarkerFaceColor','g','MarkerSize',8)
xlabel('Speed [krpm]')
ylabel('Efficiency [%]')
set(gca,'FontName','Times New Roman','fontsize',12)
legend('P43-32192-sf40kHz','P43-32192-sf20kHz','P43-32192-sf60kHz','FontName','Times New Roman','fontsize',16)
grid

% subplot(2,1,2)
% hold on
% plot(mean(P43_32192_eff,1),mean(P43_32192_eff,1),'sk','MarkerFaceColor',[0 0 0])
% xlabel('Speed [rpm]')
% ylabel('Efficiency [%]')
% set(gca,'FontName','Times New Roman','fontsize',12)
% sgtitle('P43-32192','FontName','Times New Roman','fontsize',16)
% grid


%%

if Flag_salea==1

Km = 10 ;

DnT = [1 2.7 4 5.5 7.5]*10^7 ;

for qq=1:size(P43_32193,2)

    P43_32193(qq).Vab_salea =  P43_32193(qq).Salea(:,8)*Km ;
    P43_32193(qq).Vbc_salea =  P43_32193(qq).Salea(:,9)*Km ;
    P43_32193(qq).Vca_salea =  P43_32193(qq).Salea(:,7)*Km ;
    
    P43_32193(qq).Va_salea = 1/3*(P43_32193(qq).Vab_salea-P43_32193(qq).Vca_salea) ;
    P43_32193(qq).Vb_salea = 1/3*(P43_32193(qq).Vbc_salea-P43_32193(qq).Vab_salea) ;
    P43_32193(qq).Vc_salea = 1/3*(P43_32193(qq).Vca_salea-P43_32193(qq).Vbc_salea) ;
    
    P43_32193(qq).Ia_salea =  P43_32193(qq).Salea(:,4)*Km ;
    P43_32193(qq).Ib_salea =  P43_32193(qq).Salea(:,3)*Km ;
    P43_32193(qq).Ic_salea =  P43_32193(qq).Salea(:,2)*Km ;
    
    % Power = Vab.*Ia+Vbc.*Ib+Vca.*Ic ;
    
    P43_32193(qq).Pac_salea = P43_32193(qq).Va_salea.*P43_32193(qq).Ia_salea+P43_32193(qq).Vb_salea.*P43_32193(qq).Ib_salea+P43_32193(qq).Vc_salea.*P43_32193(qq).Ic_salea ;
    P43_32193(qq).Vdc_salea = P43_32193(qq).Salea(:,6)*Km ;
    P43_32193(qq).Idc_salea = -P43_32193(qq).Salea(:,5)*Km ;
    P43_32193(qq).Pdc_salea = P43_32193(qq).Vdc_salea.*P43_32193(qq).Idc_salea ;
    
    NPeriod = 1 ;
    
    clear DCcut Vcut Icut Pcut
    for i=1:length(DnT)
    
    Period_sampling = 6.4*10^-7/2 ;
    P43_32193(qq).Npoint = round(P43_32193(qq).Period./Period_sampling) ;
    
    P43_32193(qq).cut(i).Vdc_salea = P43_32193(qq).Vdc_salea(DnT(i):DnT(i)+P43_32193(qq).Npoint(i)*NPeriod) ;
    P43_32193(qq).cut(i).Idc_salea = P43_32193(qq).Idc_salea(DnT(i):DnT(i)+P43_32193(qq).Npoint(i)*NPeriod) ;
    
    P43_32193(qq).cut(i).Va_salea = P43_32193(qq).Va_salea(DnT(i):DnT(i)+P43_32193(qq).Npoint(i)*NPeriod) ;
    P43_32193(qq).cut(i).Vb_salea = P43_32193(qq).Vb_salea(DnT(i):DnT(i)+P43_32193(qq).Npoint(i)*NPeriod) ;
    P43_32193(qq).cut(i).Vc_salea = P43_32193(qq).Vc_salea(DnT(i):DnT(i)+P43_32193(qq).Npoint(i)*NPeriod) ;

    P43_32193(qq).cut(i).Ia_salea = P43_32193(qq).Ia_salea(DnT(i):DnT(i)+P43_32193(qq).Npoint(i)*NPeriod) ;
    P43_32193(qq).cut(i).Ib_salea = P43_32193(qq).Ib_salea(DnT(i):DnT(i)+P43_32193(qq).Npoint(i)*NPeriod) ;
    P43_32193(qq).cut(i).Ic_salea = P43_32193(qq).Ic_salea(DnT(i):DnT(i)+P43_32193(qq).Npoint(i)*NPeriod) ;

    P43_32193(qq).Vdc_mean_salea(i)= mean(P43_32193(qq).cut(i).Vdc_salea) ;
    P43_32193(qq).Idc_mean_salea(i) =mean(P43_32193(qq).cut(i).Idc_salea) ;
    
    P43_32193(qq).Va_rms_salea(i) = sqrt(1/length(P43_32193(qq).cut(i).Va_salea)*sum(P43_32193(qq).cut(i).Va_salea.^2)) ;
    P43_32193(qq).Vb_rms_salea(i) = sqrt(1/length(P43_32193(qq).cut(i).Vb_salea)*sum(P43_32193(qq).cut(i).Vb_salea.^2)) ;
    P43_32193(qq).Vc_rms_salea(i) = sqrt(1/length(P43_32193(qq).cut(i).Vc_salea)*sum(P43_32193(qq).cut(i).Vc_salea.^2)) ;
    
    P43_32193(qq).Ia_rms_salea(i) = sqrt(1/length(P43_32193(qq).cut(i).Ia_salea)*sum(P43_32193(qq).cut(i).Ia_salea.^2)) ;
    P43_32193(qq).Ib_rms_salea(i) = sqrt(1/length(P43_32193(qq).cut(i).Ib_salea)*sum(P43_32193(qq).cut(i).Ib_salea.^2)) ;
    P43_32193(qq).Ic_rms_salea(i) = sqrt(1/length(P43_32193(qq).cut(i).Ic_salea)*sum(P43_32193(qq).cut(i).Ic_salea.^2)) ;
    
    [P43_32193(qq).fft(i).AmpVa,P43_32193(qq).fft(i).AngVa,P43_32193(qq).fft(i).FunVa] = FFT(P43_32193(qq).cut(i).Va_salea,NPeriod) ;
    [P43_32193(qq).fft(i).AmpVb,P43_32193(qq).fft(i).AngVb,P43_32193(qq).fft(i).FunVb] = FFT(P43_32193(qq).cut(i).Vb_salea,NPeriod) ;
    [P43_32193(qq).fft(i).AmpVc,P43_32193(qq).fft(i).AngVc,P43_32193(qq).fft(i).FunVc] = FFT(P43_32193(qq).cut(i).Vc_salea,NPeriod) ;
    
    [P43_32193(qq).fft(i).AmpIa,P43_32193(qq).fft(i).AngIa,P43_32193(qq).fft(i).FunIa] = FFT(P43_32193(qq).cut(i).Ia_salea,NPeriod) ;
    [P43_32193(qq).fft(i).AmpIb,P43_32193(qq).fft(i).AngIb,P43_32193(qq).fft(i).FunIb] = FFT(P43_32193(qq).cut(i).Ib_salea,NPeriod) ;
    [P43_32193(qq).fft(i).AmpIc,P43_32193(qq).fft(i).AngIc,P43_32193(qq).fft(i).FunIc] = FFT(P43_32193(qq).cut(i).Ic_salea,NPeriod) ;
    
    P43_32193(qq).PFa(i) = cos(P43_32193(qq).fft(i).AngVa(NPeriod)-P43_32193(qq).fft(i).AngIa(NPeriod));
    P43_32193(qq).PFb(i) = cos(P43_32193(qq).fft(i).AngVb(NPeriod)-P43_32193(qq).fft(i).AngIb(NPeriod));
    P43_32193(qq).PFc(i) = cos(P43_32193(qq).fft(i).AngVc(NPeriod)-P43_32193(qq).fft(i).AngIc(NPeriod));
    
    % Pcut(i).Power    = Power(DnT(i):DnT(i)+Npoint(i)*NPeriod) ;
    P43_32193(qq).cut(i).Pac_salea    = P43_32193(qq).Pac_salea(DnT(i):DnT(i)+P43_32193(qq).Npoint(i)*NPeriod) ;
    P43_32193(qq).cut(i).Pac_fh_salea = P43_32193(qq).fft(i).FunVa.*P43_32193(qq).fft(i).FunIa+P43_32193(qq).fft(i).FunVb.*P43_32193(qq).fft(i).FunIb+P43_32193(qq).fft(i).FunVc.*P43_32193(qq).fft(i).FunIc  ;
    P43_32193(qq).cut(i).Pdc_salea   = P43_32193(qq).Pdc_salea(DnT(i):DnT(i)+P43_32193(qq).Npoint(i)*NPeriod) ;
    
    % Pcut(i).AC_power_mean = mean(Pcut(i).Power) ;
    P43_32193(qq).Pac_mean_salea(i) = mean(P43_32193(qq).cut(i).Pac_salea) ;
    P43_32193(qq).Pac_fh_mean_salea(i) = mean(P43_32193(qq).cut(i).Pac_fh_salea) ;
    P43_32193(qq).Pdc_mean_salea(i) = mean(P43_32193(qq).cut(i).Pdc_salea) ;
    % Pcut(i).Electronic_losses = Pcut(i).DC_power_mean - Pcut(i).AC_power_mean;
    
    % P43(qq).Pcut(i).DC_rms = P43(qq).DCcut(i).Vdcrms*P43(qq).DCcut(i).Idcrms;
    % P43(qq).Pcut(i).AC_rms = P43(qq).cut(i).Va_salearms*P43(qq).cut(i).Ia_salearms+P43(qq).cut(i).Vb_salearms*P43(qq).cut(i).Ib_salearms+P43(qq).cut(i).Vc_salearms*P43(qq).cut(i).Ic_salearms;
    % P43(qq).Pcut(i).Electronic_losses_rms = P43(qq).Pcut(i).DC_rms - P43(qq).Pcut(i).AC_rms ;
    
    end

    P43_32193(qq).Eff_drive_salea = (P43_32193(qq).Power_Mech./P43_32193(qq).Pdc_mean_salea)*100 ;
    P43_32193(qq).Eff_motor = (P43_32193(qq).Power_Mech./P43_32193(qq).Pac_mean_salea)*100 ;
    P43_32193(qq).Eff_electronic = (P43_32193(qq).Pac_mean_salea./P43_32193(qq).Pdc_mean_salea)*100 ;

end



for qq=1:size(P43_32193,2)
figure
subplot(2,2,[1 2])
bar(P43_32193(qq).Speed_mean/1000,[P43_32193(qq).Eff_drive_tyto; P43_32193(qq).Eff_drive_salea])
xticks(round(P43_32193(qq).Speed_mean)/1000)
set(gca,'FontName','Times New Roman','fontsize',10)
ylabel('Eff [%]')
xlabel('Speed [krpm]')
ylim([30 100])
legend('tyto','salea')
grid
t=title(P43_32193(qq).Name);
set(t,'Units','normalized')
set(t, 'Position', [0.07 1 0])
subplot(2,2,3)
bar(P43_32193(qq).Speed_mean/1000,[P43_32193(qq).Idc_mean_tyto; P43_32193(qq).Idc_mean_salea])
xticks(round(P43_32193(qq).Speed_mean)/1000)
set(gca,'FontName','Times New Roman','fontsize',10)
ylabel('Idc [A]')
xlabel('Speed [krpm]')
% ylim([30 100])
grid
subplot(2,2,4)
bar(P43_32193(qq).Speed_mean/1000,[P43_32193(qq).Vdc_mean_tyto; P43_32193(qq).Vdc_mean_salea])
xticks(round(P43_32193(qq).Speed_mean)/1000)
set(gca,'FontName','Times New Roman','fontsize',10)
ylabel('Vdc [V]')
xlabel('Speed [krpm]')
% ylim([30 100])
grid
end
% h=legend('Power train tyto','FontName','Times New Roman','fontsize',12,'Orientation','horizontal');
% set(h, 'Units','normalized', 'Position',[0.5 0.93 0.1 0.05]);


% figure
% hold on
% plot(P43(1).Idc_tyto)
% for i=1:length(DnT)
% plot([DnT(i) DnT(i)],[-50 100],'k')
% plot([DnT(i)+P43(1).Npoint(i)*NPeriod DnT(i)+P43(1).Npoint(i)*NPeriod],[-50 100],'k')
% end
% ylabel('Idc [A]');xlabel('Samples')
% set(gca,'FontName','Times New Roman','fontsize',FontS)
% grid

% for qq=1:size(P43,2)
% 
%     figure
%     subplot(3,2,1);hold on
%     plot(P43(qq).Va)
%     for i=1:length(DnT)
%     plot([DnT(i) DnT(i)],[-50 100],'k')
%     plot([DnT(i)+P43(qq).Npoint(i)*NPeriod DnT(i)+P43(qq).Npoint(i)*NPeriod],[-50 100],'k')
%     end
%     ylabel('Va [V]');xlabel('Samples')
%     set(gca,'FontName','Times New Roman','fontsize',FontS)
%     grid
% 
%     subplot(3,2,3);hold on
%     plot(P43(qq).Ia)
%     for i=1:length(DnT)
%     plot([DnT(i) DnT(i)],[-50 100],'k')
%     plot([DnT(i)+P43(qq).Npoint(i)*NPeriod DnT(i)+P43(qq).Npoint(i)*NPeriod],[-50 100],'k')
%     end
%     ylabel('Ia [A]');xlabel('Samples');%ylim([15 20])
%     set(gca,'FontName','Times New Roman','fontsize',FontS)
%     grid
% 
%     subplot(3,2,5);hold on
%     plot(P43(qq).PowerPh)
%     for i=1:length(DnT)
%     plot([DnT(i) DnT(i)],[-50 2000],'k')
%     plot([DnT(i)+P43(qq).Npoint(i)*NPeriod DnT(i)+P43(qq).Npoint(i)*NPeriod],[-50 100],'k')
%     end
%     ylabel('Pac [W]');xlabel('Samples');%ylim([15 2000])
%     set(gca,'FontName','Times New Roman','fontsize',FontS)
%     grid
% 
%     subplot(3,2,2);hold on
%     plot(P43(qq).Idc)
%     for i=1:length(DnT)
%     plot([DnT(i) DnT(i)],[-50 100],'k')
%     plot([DnT(i)+P43(qq).Npoint(i)*NPeriod DnT(i)+P43(qq).Npoint(i)*NPeriod],[-50 100],'k')
%     end
%     ylabel('Idc [A]');xlabel('Samples')
%     set(gca,'FontName','Times New Roman','fontsize',FontS)
%     grid
% 
%     subplot(3,2,4);hold on
%     plot(P43(qq).Vdc)
%     for i=1:length(DnT)
%     plot([DnT(i) DnT(i)],[-50 100],'k')
%     plot([DnT(i)+P43(qq).Npoint(i)*NPeriod DnT(i)+P43(qq).Npoint(i)*NPeriod],[-50 100],'k')
%     end
%     ylabel('Vdc [V]');xlabel('Samples');%ylim([15 20])
%     set(gca,'FontName','Times New Roman','fontsize',FontS)
%     grid
% 
%     subplot(3,2,6);hold on
%     plot(P43(qq).Power_dc)
%     for i=1:length(DnT)
%     plot([DnT(i) DnT(i)],[-50 2000],'k')
%     plot([DnT(i)+P43(qq).Npoint(i)*NPeriod DnT(i)+P43(qq).Npoint(i)*NPeriod],[-50 100],'k')
%     end
%     ylabel('Pdc [W]');xlabel('Samples');%ylim([15 2000])
%     set(gca,'FontName','Times New Roman','fontsize',FontS)
%     grid
% 
%     sgtitle('Salea mesurements MGM','FontName','Times New Roman','fontsize',FontS+2)
% 
% end


for qq=1:size(P43_32193,2)
    for i=1:length(DnT)

    figure
    subplot(3,3,1);hold on
    plot(P43_32193(qq).cut(i).Va_salea,'b','LineWidth',1.5)
    % plot(cut(i).Va_saleab,'k','LineWidth',1.5)
    % plot(Vcut(i).FunVab,'r','LineWidth',1.5)
    set(gca,'FontName','Times New Roman','fontsize',FontS)
    xlabel('Samples');ylabel('PhA [V]');grid

    subplot(3,3,2);hold on
    plot(P43_32193(qq).cut(i).Vb_salea,'b','LineWidth',1.5)
    % plot(Vcut(i).FunVbc,'r','LineWidth',1.5)
    set(gca,'FontName','Times New Roman','fontsize',FontS)
    xlabel('Samples');ylabel('PhB [V]');grid

    subplot(3,3,3);hold on
    plot(P43_32193(qq).cut(i).Vc_salea,'b','LineWidth',1.5)
    % plot(Vcut(i).FunVca,'r','LineWidth',1.5)
    set(gca,'FontName','Times New Roman','fontsize',FontS)
    xlabel('Samples');ylabel('PhC [V]');grid

    subplot(3,3,4);hold on
    plot(P43_32193(qq).cut(i).Ia_salea,'b','LineWidth',1.5)
    % plot(Icut(i).FunIa,'r','LineWidth',1.5)
    set(gca,'FontName','Times New Roman','fontsize',FontS)
    xlabel('Samples');ylabel('PhA [A]');grid

    subplot(3,3,5);hold on
    plot(P43_32193(qq).cut(i).Ib_salea,'b','LineWidth',1.5)
    % plot(Icut(i).FunIb,'r','LineWidth',1.5)
    set(gca,'FontName','Times New Roman','fontsize',FontS)
    xlabel('Samples');ylabel('PhB [A]');grid

    subplot(3,3,6);hold on
    plot(P43_32193(qq).cut(i).Ic_salea,'b','LineWidth',1.5)
    % plot(Icut(i).FunIc,'r','LineWidth',1.5)
    set(gca,'FontName','Times New Roman','fontsize',FontS)
    set(gca,'FontName','Times New Roman','fontsize',FontS)
    xlabel('Samples');ylabel('PhC [A]');grid

    subplot(3,3,[7 9]);hold on
    plot(P43_32193(qq).Pcut(i).PowerPh,'b','LineWidth',1.5)
    plot([0 size(P43_32193(qq).Pcut(i).PowerPh,1)],[mean(P43_32193(qq).Pcut(i).PowerPh) mean(P43_32193(qq).Pcut(i).PowerPh)],'g','LineWidth',1.5)
    plot(P43_32193(qq).Pcut(i).Pdc_salea,'r','LineWidth',1.5)
    set(gca,'FontName','Times New Roman','fontsize',FontS)
    set(gca,'FontName','Times New Roman','fontsize',FontS)
    xlabel('Samples');ylabel('Power [W]');grid

    end

end



% close all
% for qq=1:size(P43_32193,2)
%     for i=1:length(DnT)
% 
%     % figure
%     % subplot(3,3,1);hold on
%     % plot(ARC(qq).cut(i).Va_salea,'b','LineWidth',1.5)
%     % % plot(cut(i).Va_saleab,'k','LineWidth',1.5)
%     % % plot(Vcut(i).FunVab,'r','LineWidth',1.5)
%     % set(gca,'FontName','Times New Roman','fontsize',FontS)
%     % xlabel('Samples');ylabel('PhA [V]');grid
%     % 
%     % subplot(3,3,2);hold on
%     % plot(ARC(qq).cut(i).Vb_salea,'b','LineWidth',1.5)
%     % % plot(Vcut(i).FunVbc,'r','LineWidth',1.5)
%     % set(gca,'FontName','Times New Roman','fontsize',FontS)
%     % xlabel('Samples');ylabel('PhB [V]');grid
%     % 
%     % subplot(3,3,3);hold on
%     % plot(ARC(qq).cut(i).Vc_salea,'b','LineWidth',1.5)
%     % % plot(Vcut(i).FunVca,'r','LineWidth',1.5)
%     % set(gca,'FontName','Times New Roman','fontsize',FontS)
%     % xlabel('Samples');ylabel('PhC [V]');grid
%     % 
%     % subplot(3,3,4);hold on
%     % plot(ARC(qq).cut(i).Ia_salea,'b','LineWidth',1.5)
%     % % plot(Icut(i).FunIa,'r','LineWidth',1.5)
%     % set(gca,'FontName','Times New Roman','fontsize',FontS)
%     % xlabel('Samples');ylabel('PhA [A]');grid
%     % 
%     % subplot(3,3,5);hold on
%     % plot(ARC(qq).cut(i).Ib_salea,'b','LineWidth',1.5)
%     % % plot(Icut(i).FunIb,'r','LineWidth',1.5)
%     % set(gca,'FontName','Times New Roman','fontsize',FontS)
%     % xlabel('Samples');ylabel('PhB [A]');grid
%     % 
%     % subplot(3,3,6);hold on
%     % plot(ARC(qq).cut(i).Ic_salea,'b','LineWidth',1.5)
%     % % plot(Icut(i).FunIc,'r','LineWidth',1.5)
%     % set(gca,'FontName','Times New Roman','fontsize',FontS)
%     % set(gca,'FontName','Times New Roman','fontsize',FontS)
%     % xlabel('Samples');ylabel('PhC [A]');grid
%     % 
%     % subplot(3,3,[7 9]);hold on
%     % plot(ARC(qq).Pcut(i).PowerPh,'b','LineWidth',1.5)
%     % plot([0 size(ARC(qq).Pcut(i).PowerPh,1)],[mean(ARC(qq).Pcut(i).PowerPh) mean(ARC(qq).Pcut(i).PowerPh)],'g','LineWidth',1.5)
%     % plot(ARC(qq).Pcut(i).Power_dc,'r','LineWidth',1.5)
%     % set(gca,'FontName','Times New Roman','fontsize',FontS)
%     % set(gca,'FontName','Times New Roman','fontsize',FontS)
%     % xlabel('Samples');ylabel('Power [W]');grid
% 
%     figure
%     subplot(2,2,1)
%     plot(P43_32193(qq).cut(i).Ia_salea,'b','LineWidth',1.5)
%     set(gca,'FontName','Times New Roman','fontsize',FontS)
%     xlabel('Samples');ylabel('PhA [A]');grid
%     subplot(2,2,2)
%     plot(P43_32193(qq).cut(i).Va_salea,'b','LineWidth',1.5)
%     set(gca,'FontName','Times New Roman','fontsize',FontS)
%     xlabel('Samples');ylabel('PhA [V]');grid
%     subplot(2,2,3)
%     b=bar(P43_32193(qq).Freq(i)*[1:size(P43_32193(qq).fft(i).AmpIa,1)]/1000,P43_32193(qq).fft(i).AmpIa);
%     xlabel('Harmonic order');ylabel('Amplitude [A]');grid
%     set(gca,'FontName','Times New Roman','fontsize',FontS)
%     xlim([P43_32193(qq).Freq(i)-10 P43_32193(qq).Freq(i)*200]/1000)
%     grid
%     subplot(2,2,4)
%     b=bar(P43_32193(qq).Freq(i)*[1:size(P43_32193(qq).fft(i).AmpIa,1)]/1000,P43_32193(qq).Vcut(i).AmpVa);
%     xlabel('Harmonic order');ylabel('Amplitude [V]');grid
%     set(gca,'FontName','Times New Roman','fontsize',FontS)
%     xlim([P43_32193(qq).Freq(i)-10 P43_32193(qq).Freq(i)*200]/1000)
%     grid
% 
%     end
% 
% end


% figure
% for qq=1:size(MGM,2)
% subplot(2,1,qq)
% bar(MGM(qq).Speed_mean,[MGM(qq).Power_Mech;[MGM(qq).Pcut.AC_powerPH_mean];[MGM(qq).Pcut.DC_power_mean];MGM(qq).Power_DC_mean]')
% xticks(round(MGM(qq).Speed_mean))
% set(gca,'FontName','Times New Roman','fontsize',12)
% ylabel('Power [W]')
% title(MGM(qq).Name)
% ylim([0 2000])
% grid
% end
% h=legend('Shaft Power','AC bus power','DC bus power','DC bus power tyto','FontName','Times New Roman','fontsize',12);
% set(h, 'Units','normalized', 'Position',[0.3 0.8 0.01 0.01]);

% figure
% for qq=1:size(P43_32193,2)
% subplot(2,1,qq)
% bar(P43_32193(qq).Speed_mean,[P43_32193(qq).Eff_drive_salea; P43_32193(qq).Eff_drive_tyto ;P43_32193(qq).Eff_motor; P43_32193(qq).Eff_electronic])
% xticks(round(P43_32193(qq).Speed_mean))
% set(gca,'FontName','Times New Roman','fontsize',12)
% ylabel('Eff [%]')
% xlabel('Speed [rpm]')
% ylim([30 100])
% grid
% t=title(P43_32193(qq).Name);
% set(t,'Units','normalized')
% set(t, 'Position', [0.07 1 0])
% end
% h=legend('Power train','Power train tyto','Motor','Electronic','FontName','Times New Roman','fontsize',12,'Orientation','horizontal');
% set(h, 'Units','normalized', 'Position',[0.5 0.93 0.1 0.05]);
% 
% 
% figure
% for qq=1:size(ARC,2)
% subplot(2,1,qq)
% bar(ARC(qq).Speed_mean,[ARC(qq).Eff_drive; ARC(qq).Eff_motor; ARC(qq).Eff_electronic])
% xticks(round(ARC(qq).Speed_mean))
% set(gca,'FontName','Times New Roman','fontsize',12)
% ylabel('Eff [%]')
% xlabel('Speed [rpm]')
% ylim([30 90])
% grid
% t=title(ARC(qq).Name);
% set(t,'Units','normalized')
% set(t, 'Position', [0.07 1 0])
% end
% h=legend('Power train','Motor','Electronic','FontName','Times New Roman','fontsize',12,'Orientation','horizontal');
% set(h, 'Units','normalized', 'Position',[0.5 0.93 0.1 0.05]);




end