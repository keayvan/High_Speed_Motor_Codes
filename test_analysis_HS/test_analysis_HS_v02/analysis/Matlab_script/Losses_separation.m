clear all; close all; clc

addpath Utility

% Name = 'MGM_study_3phases_steps_01\analog.csv';
% Path = 'D:\ARQUIMEA GROUP\Keayvan Keramati - phaseAnalysis\data\raw\Salea\' ;
% uiopen(fullfile(Path,Name),1)
% 
% Name = 'MGM_study_3phases_steps_01_fullRes.csv';
% Path = 'D:\ARQUIMEA GROUP\Keayvan Keramati - phaseAnalysis\data\raw\TYTO\' ;
% uiopen(fullfile(Path,Name),1)
% 
% Name = 'ARC_study_3phases_steps_03\analog.csv';
% Path = 'D:\ARQUIMEA GROUP\Keayvan Keramati - phaseAnalysis\data\raw\Salea\' ;
% uiopen(fullfile(Path,Name),1)
% 
% Name = 'ARC_study_3phases_steps_03_fullRes.csv';
% Path = 'D:\ARQUIMEA GROUP\Keayvan Keramati - phaseAnalysis\data\raw\TYTO\' ;
% uiopen(fullfile(Path,Name),1)

load('MGM.mat')
MGM(1).Name='MGM';
MGM(1).Salea=Salea; clear Salea
MGM(1).Tyto=Tyto; clear Tyto
load('MGM1.mat')
MGM(2).Name='MGM';
MGM(2).Salea=Salea; clear Salea
MGM(2).Tyto=Tyto; clear Tyto
load('ARC.mat')
ARC(1).Name='PULSAR';
ARC(1).Salea=Salea; clear Salea
ARC(1).Tyto=Tyto; clear Tyto
load('ARC1.mat')
ARC(2).Name='PULSAR';
ARC(2).Salea=Salea; clear Salea
ARC(2).Tyto=Tyto; clear Tyto

% Salea(:,2:4) =-Salea(:,2:4);



%%
%--- Tyto results
close all;clc

FontS=11;

DnT = [0.8 0.9;1.3 1.4;1.8 1.9;2.2 2.3;2.7 2.8]*10^4 ;
DnS = [0.2 0.3;0.6 0.7;1.3 1.4;2.2 2.3;3.3 3.4]*10^3 ;

for qq=1:size(MGM,2)

    MGM(qq).Torque = MGM(qq).Tyto(:,4) ;
    MGM(qq).Torque = MGM(qq).Torque(~isnan(MGM(qq).Tyto(:,4)));
    MGM(qq).Time_Torque = MGM(qq).Tyto(:,1) ;
    MGM(qq).Time_Torque = MGM(qq).Time_Torque(~isnan(MGM(qq).Tyto(:,4)));
    MGM(qq).Speed = MGM(qq).Tyto(:,7) ;
    MGM(qq).Speed = MGM(qq).Speed(~isnan(MGM(qq).Tyto(:,7)));

    MGM(qq).Idc_tyto = MGM(qq).Tyto(:,6) ;
    MGM(qq).Vdc_tyto = MGM(qq).Tyto(:,5) ;
    MGM(qq).Pdc_tyto = MGM(qq).Vdc_tyto.*MGM(qq).Idc_tyto ;
    MGM(qq).Idc_tyto = MGM(qq).Idc_tyto(~isnan(MGM(qq).Tyto(:,6)));
    MGM(qq).Vdc_tyto = MGM(qq).Vdc_tyto(~isnan(MGM(qq).Tyto(:,5)));
    MGM(qq).Pdc_tyto = MGM(qq).Pdc_tyto(~isnan(MGM(qq).Pdc_tyto));

    for i=1:length(DnT)
    MGM(qq).Torque_mean(i) = mean(MGM(qq).Torque(DnT(i,1):DnT(i,2))) ;
    MGM(qq).Speed_mean(i)  = mean(MGM(qq).Speed(DnS(i,1):DnS(i,2))) ;
    MGM(qq).Idc_mean(i)   = mean(MGM(qq).Idc_tyto(DnT(i,1):DnT(i,2))) ;
    MGM(qq).Vdc_mean(i)   = mean(MGM(qq).Vdc_tyto(DnT(i,1):DnT(i,2))) ;
    MGM(qq).Power_Mech(i)  = MGM(qq).Torque_mean(i)*MGM(qq).Speed_mean(i)*2*pi/60 ;
    MGM(qq).Power_DC_mean(i)  = MGM(qq).Idc_mean(i)*MGM(qq).Vdc_mean(i) ;
    end 

    MGM(qq).Freq = MGM(qq).Speed_mean*5/60 ;
    MGM(qq).Period = 1./MGM(qq).Freq ;
    MGM(qq).Eff_drive_tyto = (MGM(qq).Power_Mech./[MGM(qq).Pdc_tyto])*100 ;

end

for qq=1:size(ARC,2)

    ARC(qq).Torque = ARC(qq).Tyto(:,4) ;
    ARC(qq).Torque = ARC(qq).Torque(~isnan(ARC(qq).Tyto(:,4)));
    ARC(qq).Time_Torque = ARC(qq).Tyto(:,1) ;
    ARC(qq).Time_Torque = ARC(qq).Time_Torque(~isnan(ARC(qq).Tyto(:,4)));
    ARC(qq).Speed = ARC(qq).Tyto(:,7) ;
    ARC(qq).Speed = ARC(qq).Speed(~isnan(ARC(qq).Tyto(:,7)));
    ARC(qq).Idc_tyto = ARC(qq).Tyto(:,6) ;
    ARC(qq).Vdc_tyto = ARC(qq).Tyto(:,5) ;
    ARC(qq).Pdc_tyto = ARC(qq).Vdc_tyto.*ARC(qq).Idc_tyto ;
    ARC(qq).Idc_tyto = ARC(qq).Idc_tyto(~isnan(ARC(qq).Tyto(:,6)));
    ARC(qq).Vdc_tyto = ARC(qq).Vdc_tyto(~isnan(ARC(qq).Tyto(:,5)));
    ARC(qq).Pdc_tyto = ARC(qq).Pdc_tyto(~isnan(ARC(qq).Pdc_tyto));

    for i=1:length(DnT)
    ARC(qq).Torque_mean(i) = mean(ARC(qq).Torque(DnT(i,1):DnT(i,2))) ;
    ARC(qq).Speed_mean(i)  = mean(ARC(qq).Speed(DnS(i,1):DnS(i,2))) ;
    ARC(qq).Idc_mean(i)   = mean(ARC(qq).Idc_tyto(DnT(i,1):DnT(i,2))) ;
    ARC(qq).Vdc_mean(i)   = mean(ARC(qq).Vdc_tyto(DnT(i,1):DnT(i,2))) ;
    ARC(qq).Power_Mech(i)  = ARC(qq).Torque_mean(i)*ARC(qq).Speed_mean(i)*2*pi/60 ;
    ARC(qq).Power_DC_mean(i)  = ARC(qq).Idc_mean(i)*ARC(qq).Vdc_mean(i) ;
    end 

    ARC(qq).Freq = ARC(qq).Speed_mean*5/60 ;
    ARC(qq).Period = 1./ARC(qq).Freq ;
    ARC(qq).Eff_drive_tyto = (ARC(qq).Power_Mech./[ARC(qq).Pdc_tyto])*100 ;

end


% for qq=1:size(MGM,2)
% 
% figure
% subplot(2,3,1);hold on
% plot(MGM(qq).Torque)
% for i=1:length(DnT)
% plot([DnT(i,1) DnT(i,1)],[-1 1],'k')
% plot([DnT(i,2) DnT(i,2)],[-1 1],'k')
% end
% ylabel('Torque [Nm]');xlabel('Samples')
% set(gca,'FontName','Times New Roman','fontsize',FontS)
% grid
% subplot(2,3,2);hold on
% plot(MGM(qq).Speed)
% for i=1:length(DnT)
% plot([DnS(i,1) DnS(i,1)],[-1 15000],'k')
% plot([DnS(i,2) DnS(i,2)],[-1 15000],'k')
% end
% ylabel('Speed [rpm]');xlabel('Samples')
% set(gca,'FontName','Times New Roman','fontsize',FontS)
% grid
% subplot(2,3,3);hold on
% plot(MGM(qq).I_DC)
% for i=1:length(DnT)
% plot([DnT(i,1) DnT(i,1)],[-1 2000],'k')
% plot([DnT(i,2) DnT(i,2)],[-1 2000],'k')
% end
% ylabel('Pdc [W]');xlabel('Samples')
% set(gca,'FontName','Times New Roman','fontsize',FontS)
% grid
% 
% subplot(2,2,3);hold on
% plot(MGM(qq).Speed_mean/1000,MGM(qq).Torque_mean,'-ob','LineWidth',1,'MarkerSize',6,'MarkerFaceColor',[1 1 1])
% ylabel('Torque [Nm]');xlabel('Speed [krpm]')
% set(gca,'FontName','Times New Roman','fontsize',FontS)
% grid
% subplot(2,2,4);hold on
% plot(MGM(qq).Speed_mean/1000,MGM(qq).Power_Mech,'-ob','LineWidth',1,'MarkerSize',6,'MarkerFaceColor',[1 1 1])
% ylabel('Power [W]');xlabel('Speed [krpm]')
% set(gca,'FontName','Times New Roman','fontsize',FontS)
% grid
% 
% sgtitle('Tyto measurements','FontName','Times New Roman','fontsize',FontS+2)
% 
% end

for qq=1:size(MGM,2)

figure
subplot(2,2,1);hold on
plot(MGM(qq).Torque)
for i=1:length(DnT)
plot([DnT(i,1) DnT(i,1)],[-1 1],'k')
plot([DnT(i,2) DnT(i,2)],[-1 1],'k')
end
ylabel('Torque [Nm]');xlabel('Samples')
set(gca,'FontName','Times New Roman','fontsize',FontS)
grid
subplot(2,2,2);hold on
plot(MGM(qq).Speed)
for i=1:length(DnT)
plot([DnS(i,1) DnS(i,1)],[-1 15000],'k')
plot([DnS(i,2) DnS(i,2)],[-1 15000],'k')
end
ylabel('Speed [rpm]');xlabel('Samples')
set(gca,'FontName','Times New Roman','fontsize',FontS)
grid
subplot(2,2,3);hold on
plot(MGM(qq).Idc_tyto)
for i=1:length(DnT)
plot([DnT(i,1) DnT(i,1)],[-1 100],'k')
plot([DnT(i,2) DnT(i,2)],[-1 100],'k')
end
ylabel('Idc [A]');xlabel('Samples')
set(gca,'FontName','Times New Roman','fontsize',FontS)
grid
subplot(2,2,4);hold on
plot(MGM(qq).Pdc_tyto)
for i=1:length(DnT)
plot([DnT(i,1) DnT(i,1)],[-1 2000],'k')
plot([DnT(i,2) DnT(i,2)],[-1 2000],'k')
end
ylabel('Pdc [W]');xlabel('Samples')
set(gca,'FontName','Times New Roman','fontsize',FontS)
grid

sgtitle('Tyto measurements','FontName','Times New Roman','fontsize',FontS+2)

end


for qq=1:size(ARC,2)

figure
subplot(2,2,1);hold on
plot(ARC(qq).Torque)
for i=1:length(DnT)
plot([DnT(i,1) DnT(i,1)],[-1 1],'k')
plot([DnT(i,2) DnT(i,2)],[-1 1],'k')
end
ylabel('Torque [Nm]');xlabel('Samples')
set(gca,'FontName','Times New Roman','fontsize',FontS)
grid
subplot(2,2,2);hold on
plot(ARC(qq).Speed)
for i=1:length(DnT)
plot([DnS(i,1) DnS(i,1)],[-1 15000],'k')
plot([DnS(i,2) DnS(i,2)],[-1 15000],'k')
end
ylabel('Speed [rpm]');xlabel('Samples')
set(gca,'FontName','Times New Roman','fontsize',FontS)
grid
subplot(2,2,3);hold on
plot(ARC(qq).Idc_tyto)
for i=1:length(DnT)
plot([DnT(i,1) DnT(i,1)],[-1 100],'k')
plot([DnT(i,2) DnT(i,2)],[-1 100],'k')
end
ylabel('Idc [A]');xlabel('Samples')
set(gca,'FontName','Times New Roman','fontsize',FontS)
grid
subplot(2,2,4);hold on
plot(ARC(qq).Pdc_tyto)
for i=1:length(DnT)
plot([DnT(i,1) DnT(i,1)],[-1 2000],'k')
plot([DnT(i,2) DnT(i,2)],[-1 2000],'k')
end
ylabel('Pdc [W]');xlabel('Samples')
set(gca,'FontName','Times New Roman','fontsize',FontS)
grid

sgtitle('Tyto measurements','FontName','Times New Roman','fontsize',FontS+2)

end





%%
%--- ASLI results
% close all;clc
clc

Km = 10 ;

DnT = [1 1.8 2.7 3.5 4]*10^7 ;

for qq=1:size(MGM,2)

    MGM(qq).Vab =  MGM(qq).Salea(:,8)*Km ;
    MGM(qq).Vbc =  MGM(qq).Salea(:,9)*Km ;
    MGM(qq).Vca =  MGM(qq).Salea(:,7)*Km ;
    
    MGM(qq).Va = 1/3*(MGM(qq).Vab-MGM(qq).Vca) ;
    MGM(qq).Vb = 1/3*(MGM(qq).Vbc-MGM(qq).Vab) ;
    MGM(qq).Vc = 1/3*(MGM(qq).Vca-MGM(qq).Vbc) ;
    
    MGM(qq).Ia =  MGM(qq).Salea(:,4)*Km ;
    MGM(qq).Ib =  MGM(qq).Salea(:,3)*Km ;
    MGM(qq).Ic =  MGM(qq).Salea(:,2)*Km ;
    
    % Power = Vab.*Ia+Vbc.*Ib+Vca.*Ic ;
    
    MGM(qq).PowerPh = MGM(qq).Va.*MGM(qq).Ia+MGM(qq).Vb.*MGM(qq).Ib+MGM(qq).Vc.*MGM(qq).Ic ;
    MGM(qq).Vdc =  MGM(qq).Salea(:,6)*Km ;
    MGM(qq).Idc = -MGM(qq).Salea(:,5)*Km ;
    MGM(qq).Power_dc = MGM(qq).Vdc.*MGM(qq).Idc ;
    
    NPeriod = 1 ;
    
    clear DCcut Vcut Icut Pcut
    for i=1:length(DnT)
    
    Period_sampling = 6.4*10^-7 ;
    MGM(qq).Npoint = round(MGM(qq).Period./Period_sampling) ;
    
    MGM(qq).DCcut(i).Vdc = MGM(qq).Vdc(DnT(i):DnT(i)+MGM(qq).Npoint(i)*NPeriod) ;
    MGM(qq).DCcut(i).Idc = MGM(qq).Idc(DnT(i):DnT(i)+MGM(qq).Npoint(i)*NPeriod) ;
    
    MGM(qq).DCcut(i).Vdcrms = sqrt(1/length(MGM(qq).DCcut(i).Vdc)*sum(MGM(qq).DCcut(i).Vdc.^2)) ;
    MGM(qq).DCcut(i).Idcrms = sqrt(1/length(MGM(qq).DCcut(i).Idc)*sum(MGM(qq).DCcut(i).Idc.^2)) ;
    
    MGM(qq).Vcut(i).Vab = MGM(qq).Vab(DnT(i):DnT(i)+MGM(qq).Npoint(i)*NPeriod) ;
    
    MGM(qq).Vcut(i).Va = MGM(qq).Va(DnT(i):DnT(i)+MGM(qq).Npoint(i)*NPeriod) ;
    MGM(qq).Vcut(i).Vb = MGM(qq).Vb(DnT(i):DnT(i)+MGM(qq).Npoint(i)*NPeriod) ;
    MGM(qq).Vcut(i).Vc = MGM(qq).Vc(DnT(i):DnT(i)+MGM(qq).Npoint(i)*NPeriod) ;
    
    MGM(qq).Vcut(i).Varms = sqrt(1/length(MGM(qq).Vcut(i).Va)*sum(MGM(qq).Vcut(i).Va.^2)) ;
    MGM(qq).Vcut(i).Vbrms = sqrt(1/length(MGM(qq).Vcut(i).Vb)*sum(MGM(qq).Vcut(i).Vb.^2)) ;
    MGM(qq).Vcut(i).Vcrms = sqrt(1/length(MGM(qq).Vcut(i).Vc)*sum(MGM(qq).Vcut(i).Vc.^2)) ;
    
    MGM(qq).Icut(i).Ia = MGM(qq).Ia(DnT(i):DnT(i)+MGM(qq).Npoint(i)*NPeriod) ;
    MGM(qq).Icut(i).Ib = MGM(qq).Ib(DnT(i):DnT(i)+MGM(qq).Npoint(i)*NPeriod) ;
    MGM(qq).Icut(i).Ic = MGM(qq).Ic(DnT(i):DnT(i)+MGM(qq).Npoint(i)*NPeriod) ;
    
    MGM(qq).Icut(i).Iarms = sqrt(1/length(MGM(qq).Icut(i).Ia)*sum(MGM(qq).Icut(i).Ia.^2)) ;
    MGM(qq).Icut(i).Ibrms = sqrt(1/length(MGM(qq).Icut(i).Ib)*sum(MGM(qq).Icut(i).Ib.^2)) ;
    MGM(qq).Icut(i).Icrms = sqrt(1/length(MGM(qq).Icut(i).Ic)*sum(MGM(qq).Icut(i).Ic.^2)) ;
    
    [MGM(qq).Vcut(i).AmpVa,MGM(qq).Vcut(i).AngVa,MGM(qq).Vcut(i).FunVa] = FFT(MGM(qq).Vcut(i).Va,NPeriod) ;
    [MGM(qq).Vcut(i).AmpVb,MGM(qq).Vcut(i).AngVb,MGM(qq).Vcut(i).FunVb] = FFT(MGM(qq).Vcut(i).Vb,NPeriod) ;
    [MGM(qq).Vcut(i).AmpVc,MGM(qq).Vcut(i).AngVc,MGM(qq).Vcut(i).FunVc] = FFT(MGM(qq).Vcut(i).Vc,NPeriod) ;
    
    [MGM(qq).Icut(i).AmpIa,MGM(qq).Icut(i).AngIa,MGM(qq).Icut(i).FunIa] = FFT(MGM(qq).Icut(i).Ia,NPeriod) ;
    [MGM(qq).Icut(i).AmpIb,MGM(qq).Icut(i).AngIb,MGM(qq).Icut(i).FunIb] = FFT(MGM(qq).Icut(i).Ib,NPeriod) ;
    [MGM(qq).Icut(i).AmpIc,MGM(qq).Icut(i).AngIc,MGM(qq).Icut(i).FunIc] = FFT(MGM(qq).Icut(i).Ic,NPeriod) ;
    
    MGM(qq).Pcut(i).PFa = cos(MGM(qq).Vcut(i).AngVa(NPeriod)-MGM(qq).Icut(i).AngIa(NPeriod));
    MGM(qq).Pcut(i).PFb = cos(MGM(qq).Vcut(i).AngVb(NPeriod)-MGM(qq).Icut(i).AngIb(NPeriod));
    MGM(qq).Pcut(i).PFc = cos(MGM(qq).Vcut(i).AngVc(NPeriod)-MGM(qq).Icut(i).AngIc(NPeriod));
    
    % Pcut(i).Power    = Power(DnT(i):DnT(i)+Npoint(i)*NPeriod) ;
    MGM(qq).Pcut(i).PowerPh  = MGM(qq).PowerPh(DnT(i):DnT(i)+MGM(qq).Npoint(i)*NPeriod) ;
    MGM(qq).Pcut(i).PowerFirstH = MGM(qq).Vcut(i).FunVa.*MGM(qq).Icut(i).FunIa+MGM(qq).Vcut(i).FunVb.*MGM(qq).Icut(i).FunIb+MGM(qq).Vcut(i).FunVc.*MGM(qq).Icut(i).FunIc  ;
    MGM(qq). Pcut(i).Power_dc = MGM(qq).Power_dc(DnT(i):DnT(i)+MGM(qq).Npoint(i)*NPeriod) ;
    
    % Pcut(i).AC_power_mean = mean(Pcut(i).Power) ;
    MGM(qq).Pcut(i).AC_powerPH_mean = mean(MGM(qq).Pcut(i).PowerPh) ;
    
    MGM(qq).Pcut(i).AC_power_meanFirstH = mean(MGM(qq).Pcut(i).PowerFirstH) ;
    MGM(qq).Pcut(i).DC_power_mean = mean(MGM(qq).Pcut(i).Power_dc) ;
    % Pcut(i).Electronic_losses = Pcut(i).DC_power_mean - Pcut(i).AC_power_mean;
    
    MGM(qq).Pcut(i).DC_rms = MGM(qq).DCcut(i).Vdcrms*MGM(qq).DCcut(i).Idcrms;
    MGM(qq).Pcut(i).AC_rms = MGM(qq).Vcut(i).Varms*MGM(qq).Icut(i).Iarms+MGM(qq).Vcut(i).Vbrms*MGM(qq).Icut(i).Ibrms+MGM(qq).Vcut(i).Vcrms*MGM(qq).Icut(i).Icrms;
    MGM(qq).Pcut(i).Electronic_losses_rms = MGM(qq).Pcut(i).DC_rms - MGM(qq).Pcut(i).AC_rms ;
    
    end

    MGM(qq).Eff_drive = (MGM(qq).Power_Mech./[MGM(qq).Pcut.DC_power_mean])*100 ;
    MGM(qq).Eff_motor = (MGM(qq).Power_Mech./[MGM(qq).Pcut.AC_powerPH_mean])*100 ;
    MGM(qq).Eff_electronic = ([MGM(qq).Pcut.AC_powerPH_mean]./[MGM(qq).Pcut.DC_power_mean])*100 ;

end

for qq=1:size(ARC,2)

    ARC(qq).Vab =  ARC(qq).Salea(:,8)*Km ;
    ARC(qq).Vbc =  ARC(qq).Salea(:,9)*Km ;
    ARC(qq).Vca =  ARC(qq).Salea(:,7)*Km ;
    
    ARC(qq).Va = 1/3*(ARC(qq).Vab-ARC(qq).Vca) ;
    ARC(qq).Vb = 1/3*(ARC(qq).Vbc-ARC(qq).Vab) ;
    ARC(qq).Vc = 1/3*(ARC(qq).Vca-ARC(qq).Vbc) ;
    
    ARC(qq).Ia =  ARC(qq).Salea(:,4)*Km ;
    ARC(qq).Ib =  ARC(qq).Salea(:,3)*Km ;
    ARC(qq).Ic =  ARC(qq).Salea(:,2)*Km ;
    
    % Power = Vab.*Ia+Vbc.*Ib+Vca.*Ic ;
    
    ARC(qq).PowerPh = ARC(qq).Va.*ARC(qq).Ia+ARC(qq).Vb.*ARC(qq).Ib+ARC(qq).Vc.*ARC(qq).Ic ;
    ARC(qq).Vdc =  ARC(qq).Salea(:,6)*Km ;
    ARC(qq).Idc = -ARC(qq).Salea(:,5)*Km ;
    ARC(qq).Power_dc = ARC(qq).Vdc.*ARC(qq).Idc ;
    
    NPeriod = 1 ;
    
    clear DCcut Vcut Icut Pcut
    for i=1:length(DnT)
    
    Period_sampling = 6.4*10^-7 ;
    ARC(qq).Npoint = round(ARC(qq).Period./Period_sampling) ;
    
    ARC(qq).DCcut(i).Vdc = ARC(qq).Vdc(DnT(i):DnT(i)+ARC(qq).Npoint(i)*NPeriod) ;
    ARC(qq).DCcut(i).Idc = ARC(qq).Idc(DnT(i):DnT(i)+ARC(qq).Npoint(i)*NPeriod) ;
    
    ARC(qq).DCcut(i).Vdcrms = sqrt(1/length(ARC(qq).DCcut(i).Vdc)*sum(ARC(qq).DCcut(i).Vdc.^2)) ;
    ARC(qq).DCcut(i).Idcrms = sqrt(1/length(ARC(qq).DCcut(i).Idc)*sum(ARC(qq).DCcut(i).Idc.^2)) ;
    
    ARC(qq).Vcut(i).Vab = ARC(qq).Vab(DnT(i):DnT(i)+ARC(qq).Npoint(i)*NPeriod) ;
    
    ARC(qq).Vcut(i).Va = ARC(qq).Va(DnT(i):DnT(i)+ARC(qq).Npoint(i)*NPeriod) ;
    ARC(qq).Vcut(i).Vb = ARC(qq).Vb(DnT(i):DnT(i)+ARC(qq).Npoint(i)*NPeriod) ;
    ARC(qq).Vcut(i).Vc = ARC(qq).Vc(DnT(i):DnT(i)+ARC(qq).Npoint(i)*NPeriod) ;
    
    ARC(qq).Vcut(i).Varms = sqrt(1/length(ARC(qq).Vcut(i).Va)*sum(ARC(qq).Vcut(i).Va.^2)) ;
    ARC(qq).Vcut(i).Vbrms = sqrt(1/length(ARC(qq).Vcut(i).Vb)*sum(ARC(qq).Vcut(i).Vb.^2)) ;
    ARC(qq).Vcut(i).Vcrms = sqrt(1/length(ARC(qq).Vcut(i).Vc)*sum(ARC(qq).Vcut(i).Vc.^2)) ;
    
    ARC(qq).Icut(i).Ia = ARC(qq).Ia(DnT(i):DnT(i)+ARC(qq).Npoint(i)*NPeriod) ;
    ARC(qq).Icut(i).Ib = ARC(qq).Ib(DnT(i):DnT(i)+ARC(qq).Npoint(i)*NPeriod) ;
    ARC(qq).Icut(i).Ic = ARC(qq).Ic(DnT(i):DnT(i)+ARC(qq).Npoint(i)*NPeriod) ;
    
    ARC(qq).Icut(i).Iarms = sqrt(1/length(ARC(qq).Icut(i).Ia)*sum(ARC(qq).Icut(i).Ia.^2)) ;
    ARC(qq).Icut(i).Ibrms = sqrt(1/length(ARC(qq).Icut(i).Ib)*sum(ARC(qq).Icut(i).Ib.^2)) ;
    ARC(qq).Icut(i).Icrms = sqrt(1/length(ARC(qq).Icut(i).Ic)*sum(ARC(qq).Icut(i).Ic.^2)) ;
    
    [ARC(qq).Vcut(i).AmpVa,ARC(qq).Vcut(i).AngVa,ARC(qq).Vcut(i).FunVa] = FFT(ARC(qq).Vcut(i).Va,NPeriod) ;
    [ARC(qq).Vcut(i).AmpVb,ARC(qq).Vcut(i).AngVb,ARC(qq).Vcut(i).FunVb] = FFT(ARC(qq).Vcut(i).Vb,NPeriod) ;
    [ARC(qq).Vcut(i).AmpVc,ARC(qq).Vcut(i).AngVc,ARC(qq).Vcut(i).FunVc] = FFT(ARC(qq).Vcut(i).Vc,NPeriod) ;
    
    [ARC(qq).Icut(i).AmpIa,ARC(qq).Icut(i).AngIa,ARC(qq).Icut(i).FunIa] = FFT(ARC(qq).Icut(i).Ia,NPeriod) ;
    [ARC(qq).Icut(i).AmpIb,ARC(qq).Icut(i).AngIb,ARC(qq).Icut(i).FunIb] = FFT(ARC(qq).Icut(i).Ib,NPeriod) ;
    [ARC(qq).Icut(i).AmpIc,ARC(qq).Icut(i).AngIc,ARC(qq).Icut(i).FunIc] = FFT(ARC(qq).Icut(i).Ic,NPeriod) ;
    
    ARC(qq).Pcut(i).PFa = cos(ARC(qq).Vcut(i).AngVa(NPeriod)-ARC(qq).Icut(i).AngIa(NPeriod));
    ARC(qq).Pcut(i).PFb = cos(ARC(qq).Vcut(i).AngVb(NPeriod)-ARC(qq).Icut(i).AngIb(NPeriod));
    ARC(qq).Pcut(i).PFc = cos(ARC(qq).Vcut(i).AngVc(NPeriod)-ARC(qq).Icut(i).AngIc(NPeriod));
    
    % Pcut(i).Power    = Power(DnT(i):DnT(i)+Npoint(i)*NPeriod) ;
    ARC(qq).Pcut(i).PowerPh  = ARC(qq).PowerPh(DnT(i):DnT(i)+ARC(qq).Npoint(i)*NPeriod) ;
    ARC(qq).Pcut(i).PowerFirstH = ARC(qq).Vcut(i).FunVa.*ARC(qq).Icut(i).FunIa+ARC(qq).Vcut(i).FunVb.*ARC(qq).Icut(i).FunIb+ARC(qq).Vcut(i).FunVc.*ARC(qq).Icut(i).FunIc  ;
    ARC(qq). Pcut(i).Power_dc = ARC(qq).Power_dc(DnT(i):DnT(i)+ARC(qq).Npoint(i)*NPeriod) ;
    
    % Pcut(i).AC_power_mean = mean(Pcut(i).Power) ;
    ARC(qq).Pcut(i).AC_powerPH_mean = mean(ARC(qq).Pcut(i).PowerPh) ;
    
    ARC(qq).Pcut(i).AC_power_meanFirstH = mean(ARC(qq).Pcut(i).PowerFirstH) ;
    ARC(qq).Pcut(i).DC_power_mean = mean(ARC(qq).Pcut(i).Power_dc) ;
    % Pcut(i).Electronic_losses = Pcut(i).DC_power_mean - Pcut(i).AC_power_mean;
    
    ARC(qq).Pcut(i).DC_rms = ARC(qq).DCcut(i).Vdcrms*ARC(qq).DCcut(i).Idcrms;
    ARC(qq).Pcut(i).AC_rms = ARC(qq).Vcut(i).Varms*ARC(qq).Icut(i).Iarms+ARC(qq).Vcut(i).Vbrms*ARC(qq).Icut(i).Ibrms+ARC(qq).Vcut(i).Vcrms*ARC(qq).Icut(i).Icrms;
    ARC(qq).Pcut(i).Electronic_losses_rms = ARC(qq).Pcut(i).DC_rms - ARC(qq).Pcut(i).AC_rms ;
    
    end

    ARC(qq).Eff_drive = (ARC(qq).Power_Mech./[ARC(qq).Pcut.DC_power_mean])*100 ;
    ARC(qq).Eff_motor = (ARC(qq).Power_Mech./[ARC(qq).Pcut.AC_powerPH_mean])*100 ;
    ARC(qq).Eff_electronic = ([ARC(qq).Pcut.AC_powerPH_mean]./[ARC(qq).Pcut.DC_power_mean])*100 ;

end



for qq=1:size(MGM,2)

    figure
    subplot(3,2,1);hold on
    plot(MGM(qq).Va)
    % for i=1:length(DnT)
    % plot([DnT(i) DnT(i)],[-50 100],'k')
    % plot([DnT(i)+MGM(qq).Npoint(i)*NPeriod DnT(i)+MGM(qq).Npoint(i)*NPeriod],[-50 100],'k')
    % end
    ylabel('Va [V]');xlabel('Samples')
    set(gca,'FontName','Times New Roman','fontsize',FontS)
    grid
    
    subplot(3,2,3);hold on
    plot(MGM(qq).Ia)
    % for i=1:length(DnT)
    % plot([DnT(i) DnT(i)],[-50 100],'k')
    % plot([DnT(i)+MGM(qq).Npoint(i)*NPeriod DnT(i)+MGM(qq).Npoint(i)*NPeriod],[-50 100],'k')
    % end
    ylabel('Ia [A]');xlabel('Samples');%ylim([15 20])
    set(gca,'FontName','Times New Roman','fontsize',FontS)
    grid

    subplot(3,2,5);hold on
    plot(MGM(qq).PowerPh)
    % for i=1:length(DnT)
    % plot([DnT(i) DnT(i)],[-50 2000],'k')
    % plot([DnT(i)+MGM(qq).Npoint(i)*NPeriod DnT(i)+MGM(qq).Npoint(i)*NPeriod],[-50 100],'k')
    % end
    ylabel('Pac [W]');xlabel('Samples');%ylim([15 2000])
    set(gca,'FontName','Times New Roman','fontsize',FontS)
    grid

    subplot(3,2,2);hold on
    plot(MGM(qq).Idc)
    % for i=1:length(DnT)
    % plot([DnT(i) DnT(i)],[-50 100],'k')
    % plot([DnT(i)+MGM(qq).Npoint(i)*NPeriod DnT(i)+MGM(qq).Npoint(i)*NPeriod],[-50 100],'k')
    % end
    ylabel('Idc [A]');xlabel('Samples')
    set(gca,'FontName','Times New Roman','fontsize',FontS)
    grid
    
    subplot(3,2,4);hold on
    plot(MGM(qq).Vdc)
    % for i=1:length(DnT)
    % plot([DnT(i) DnT(i)],[-50 100],'k')
    % plot([DnT(i)+MGM(qq).Npoint(i)*NPeriod DnT(i)+MGM(qq).Npoint(i)*NPeriod],[-50 100],'k')
    % end
    ylabel('Vdc [V]');xlabel('Samples');%ylim([15 20])
    set(gca,'FontName','Times New Roman','fontsize',FontS)
    grid

    subplot(3,2,6);hold on
    plot(MGM(qq).Power_dc)
    % for i=1:length(DnT)
    % plot([DnT(i) DnT(i)],[-50 2000],'k')
    % plot([DnT(i)+MGM(qq).Npoint(i)*NPeriod DnT(i)+MGM(qq).Npoint(i)*NPeriod],[-50 100],'k')
    % end
    ylabel('Pdc [W]');xlabel('Samples');%ylim([15 2000])
    set(gca,'FontName','Times New Roman','fontsize',FontS)
    grid
    
    sgtitle('Salea mesurements MGM','FontName','Times New Roman','fontsize',FontS+2)

end

for qq=1:size(ARC,2)

    figure
    subplot(3,2,1);hold on
    plot(ARC(qq).Va)
    % for i=1:length(DnT)
    % plot([DnT(i) DnT(i)],[-50 100],'k')
    % plot([DnT(i)+MGM(qq).Npoint(i)*NPeriod DnT(i)+MGM(qq).Npoint(i)*NPeriod],[-50 100],'k')
    % end
    ylabel('Va [V]');xlabel('Samples')
    set(gca,'FontName','Times New Roman','fontsize',FontS)
    grid
    
    subplot(3,2,3);hold on
    plot(ARC(qq).Ia)
    % for i=1:length(DnT)
    % plot([DnT(i) DnT(i)],[-50 100],'k')
    % plot([DnT(i)+MGM(qq).Npoint(i)*NPeriod DnT(i)+MGM(qq).Npoint(i)*NPeriod],[-50 100],'k')
    % end
    ylabel('Ia [A]');xlabel('Samples');%ylim([15 20])
    set(gca,'FontName','Times New Roman','fontsize',FontS)
    grid

    subplot(3,2,5);hold on
    plot(ARC(qq).PowerPh)
    % for i=1:length(DnT)
    % plot([DnT(i) DnT(i)],[-50 2000],'k')
    % plot([DnT(i)+MGM(qq).Npoint(i)*NPeriod DnT(i)+MGM(qq).Npoint(i)*NPeriod],[-50 100],'k')
    % end
    ylabel('Pac [W]');xlabel('Samples');%ylim([15 2000])
    set(gca,'FontName','Times New Roman','fontsize',FontS)
    grid

    subplot(3,2,2);hold on
    plot(ARC(qq).Idc)
    % for i=1:length(DnT)
    % plot([DnT(i) DnT(i)],[-50 100],'k')
    % plot([DnT(i)+MGM(qq).Npoint(i)*NPeriod DnT(i)+MGM(qq).Npoint(i)*NPeriod],[-50 100],'k')
    % end
    ylabel('Idc [A]');xlabel('Samples')
    set(gca,'FontName','Times New Roman','fontsize',FontS)
    grid
    
    subplot(3,2,4);hold on
    plot(ARC(qq).Vdc)
    % for i=1:length(DnT)
    % plot([DnT(i) DnT(i)],[-50 100],'k')
    % plot([DnT(i)+MGM(qq).Npoint(i)*NPeriod DnT(i)+MGM(qq).Npoint(i)*NPeriod],[-50 100],'k')
    % end
    ylabel('Vdc [V]');xlabel('Samples');%ylim([15 20])
    set(gca,'FontName','Times New Roman','fontsize',FontS)
    grid

    subplot(3,2,6);hold on
    plot(ARC(qq).Power_dc)
    % for i=1:length(DnT)
    % plot([DnT(i) DnT(i)],[-50 2000],'k')
    % plot([DnT(i)+MGM(qq).Npoint(i)*NPeriod DnT(i)+MGM(qq).Npoint(i)*NPeriod],[-50 100],'k')
    % end
    ylabel('Pdc [W]');xlabel('Samples');%ylim([15 2000])
    set(gca,'FontName','Times New Roman','fontsize',FontS)
    grid
    
    sgtitle('Salea mesurements PULSAR','FontName','Times New Roman','fontsize',FontS+2)

end


for qq=1:size(MGM,2)
    for i=1:length(DnT)
    
    figure
    subplot(3,3,1);hold on
    plot(MGM(qq).Vcut(i).Va,'b','LineWidth',1.5)
    % plot(Vcut(i).Vab,'k','LineWidth',1.5)
    % plot(Vcut(i).FunVab,'r','LineWidth',1.5)
    set(gca,'FontName','Times New Roman','fontsize',FontS)
    xlabel('Samples');ylabel('PhA [V]');grid
    
    subplot(3,3,2);hold on
    plot(MGM(qq).Vcut(i).Vb,'b','LineWidth',1.5)
    % plot(Vcut(i).FunVbc,'r','LineWidth',1.5)
    set(gca,'FontName','Times New Roman','fontsize',FontS)
    xlabel('Samples');ylabel('PhB [V]');grid
    
    subplot(3,3,3);hold on
    plot(MGM(qq).Vcut(i).Vc,'b','LineWidth',1.5)
    % plot(Vcut(i).FunVca,'r','LineWidth',1.5)
    set(gca,'FontName','Times New Roman','fontsize',FontS)
    xlabel('Samples');ylabel('PhC [V]');grid
    
    subplot(3,3,4);hold on
    plot(MGM(qq).Icut(i).Ia,'b','LineWidth',1.5)
    % plot(Icut(i).FunIa,'r','LineWidth',1.5)
    set(gca,'FontName','Times New Roman','fontsize',FontS)
    xlabel('Samples');ylabel('PhA [A]');grid
    
    subplot(3,3,5);hold on
    plot(MGM(qq).Icut(i).Ib,'b','LineWidth',1.5)
    % plot(Icut(i).FunIb,'r','LineWidth',1.5)
    set(gca,'FontName','Times New Roman','fontsize',FontS)
    xlabel('Samples');ylabel('PhB [A]');grid
    
    subplot(3,3,6);hold on
    plot(MGM(qq).Icut(i).Ic,'b','LineWidth',1.5)
    % plot(Icut(i).FunIc,'r','LineWidth',1.5)
    set(gca,'FontName','Times New Roman','fontsize',FontS)
    set(gca,'FontName','Times New Roman','fontsize',FontS)
    xlabel('Samples');ylabel('PhC [A]');grid
    
    subplot(3,3,[7 9]);hold on
    plot(MGM(qq).Pcut(i).PowerPh,'b','LineWidth',1.5)
    plot([0 size(MGM(qq).Pcut(i).PowerPh,1)],[mean(MGM(qq).Pcut(i).PowerPh) mean(MGM(qq).Pcut(i).PowerPh)],'g','LineWidth',1.5)
    plot(MGM(qq).Pcut(i).Power_dc,'r','LineWidth',1.5)
    set(gca,'FontName','Times New Roman','fontsize',FontS)
    set(gca,'FontName','Times New Roman','fontsize',FontS)
    xlabel('Samples');ylabel('Power [W]');grid
    
    end

end


%%


close all
for qq=1%:size(ARC,2)
    for i=1:length(DnT)
    
    % figure
    % subplot(3,3,1);hold on
    % plot(ARC(qq).Vcut(i).Va,'b','LineWidth',1.5)
    % % plot(Vcut(i).Vab,'k','LineWidth',1.5)
    % % plot(Vcut(i).FunVab,'r','LineWidth',1.5)
    % set(gca,'FontName','Times New Roman','fontsize',FontS)
    % xlabel('Samples');ylabel('PhA [V]');grid
    % 
    % subplot(3,3,2);hold on
    % plot(ARC(qq).Vcut(i).Vb,'b','LineWidth',1.5)
    % % plot(Vcut(i).FunVbc,'r','LineWidth',1.5)
    % set(gca,'FontName','Times New Roman','fontsize',FontS)
    % xlabel('Samples');ylabel('PhB [V]');grid
    % 
    % subplot(3,3,3);hold on
    % plot(ARC(qq).Vcut(i).Vc,'b','LineWidth',1.5)
    % % plot(Vcut(i).FunVca,'r','LineWidth',1.5)
    % set(gca,'FontName','Times New Roman','fontsize',FontS)
    % xlabel('Samples');ylabel('PhC [V]');grid
    % 
    % subplot(3,3,4);hold on
    % plot(ARC(qq).Icut(i).Ia,'b','LineWidth',1.5)
    % % plot(Icut(i).FunIa,'r','LineWidth',1.5)
    % set(gca,'FontName','Times New Roman','fontsize',FontS)
    % xlabel('Samples');ylabel('PhA [A]');grid
    % 
    % subplot(3,3,5);hold on
    % plot(ARC(qq).Icut(i).Ib,'b','LineWidth',1.5)
    % % plot(Icut(i).FunIb,'r','LineWidth',1.5)
    % set(gca,'FontName','Times New Roman','fontsize',FontS)
    % xlabel('Samples');ylabel('PhB [A]');grid
    % 
    % subplot(3,3,6);hold on
    % plot(ARC(qq).Icut(i).Ic,'b','LineWidth',1.5)
    % % plot(Icut(i).FunIc,'r','LineWidth',1.5)
    % set(gca,'FontName','Times New Roman','fontsize',FontS)
    % set(gca,'FontName','Times New Roman','fontsize',FontS)
    % xlabel('Samples');ylabel('PhC [A]');grid
    % 
    % subplot(3,3,[7 9]);hold on
    % plot(ARC(qq).Pcut(i).PowerPh,'b','LineWidth',1.5)
    % plot([0 size(ARC(qq).Pcut(i).PowerPh,1)],[mean(ARC(qq).Pcut(i).PowerPh) mean(ARC(qq).Pcut(i).PowerPh)],'g','LineWidth',1.5)
    % plot(ARC(qq).Pcut(i).Power_dc,'r','LineWidth',1.5)
    % set(gca,'FontName','Times New Roman','fontsize',FontS)
    % set(gca,'FontName','Times New Roman','fontsize',FontS)
    % xlabel('Samples');ylabel('Power [W]');grid
    
    figure
    subplot(2,2,1)
    plot(ARC(qq).Icut(i).Ia,'b','LineWidth',1.5)
    set(gca,'FontName','Times New Roman','fontsize',FontS)
    xlabel('Samples');ylabel('PhA [A]');grid
    subplot(2,2,2)
    plot(ARC(qq).Vcut(i).Va,'b','LineWidth',1.5)
    set(gca,'FontName','Times New Roman','fontsize',FontS)
    xlabel('Samples');ylabel('PhA [V]');grid
    subplot(2,2,3)
    b=bar(ARC(qq).Freq(i)*[1:size(ARC(qq).Icut(i).AmpIa,1)]/1000,ARC(qq).Icut(i).AmpIa);
    xlabel('Harmonic order');ylabel('Amplitude [A]');grid
    set(gca,'FontName','Times New Roman','fontsize',FontS)
    xlim([ARC(qq).Freq(i)-10 ARC(qq).Freq(i)*200]/1000)
    grid
    subplot(2,2,4)
    b=bar(ARC(qq).Freq(i)*[1:size(ARC(qq).Icut(i).AmpIa,1)]/1000,ARC(qq).Vcut(i).AmpVa);
    xlabel('Harmonic order');ylabel('Amplitude [V]');grid
    set(gca,'FontName','Times New Roman','fontsize',FontS)
    xlim([ARC(qq).Freq(i)-10 ARC(qq).Freq(i)*200]/1000)
    grid

    end

end



%%
close all

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

figure
for qq=1:size(MGM,2)
subplot(2,1,qq)
bar(MGM(qq).Speed_mean,[MGM(qq).Eff_drive; MGM(qq).Eff_drive_tyto ;MGM(qq).Eff_motor; MGM(qq).Eff_electronic])
xticks(round(MGM(qq).Speed_mean))
set(gca,'FontName','Times New Roman','fontsize',12)
ylabel('Eff [%]')
xlabel('Speed [rpm]')
ylim([30 90])
grid
t=title(MGM(qq).Name);
set(t,'Units','normalized')
set(t, 'Position', [0.07 1 0])
end
h=legend('Power train','Motor','Electronic','FontName','Times New Roman','fontsize',12,'Orientation','horizontal');
set(h, 'Units','normalized', 'Position',[0.5 0.93 0.1 0.05]);


figure
for qq=1:size(ARC,2)
subplot(2,1,qq)
bar(ARC(qq).Speed_mean,[ARC(qq).Eff_drive; ARC(qq).Eff_drive_tyto; ARC(qq).Eff_motor; ARC(qq).Eff_electronic])
xticks(round(ARC(qq).Speed_mean))
set(gca,'FontName','Times New Roman','fontsize',12)
ylabel('Eff [%]')
xlabel('Speed [rpm]')
ylim([30 90])
grid
t=title(ARC(qq).Name);
set(t,'Units','normalized')
set(t, 'Position', [0.07 1 0])
end
h=legend('Power train','Motor','Electronic','FontName','Times New Roman','fontsize',12,'Orientation','horizontal');
set(h, 'Units','normalized', 'Position',[0.5 0.93 0.1 0.05]);





%%

% 
% figure
% subplot(2,1,1);hold on
% plot(analog(:,2)*Km)
% for i=1:length(DnT)
% plot([DnT(i) DnT(i)],[-10 10],'k')
% plot([DnT(i)+Npoint(i) DnT(i)+Npoint(i)],[-100 100],'k')
% end
% ylabel('Ia [A]')
% grid
% for i=1:length(DnT)
% subplot(2,4,4+i);hold on
% plot(analog(DnT(i):DnT(i)+Npoint(i),2)*Km)
% end
% % ylabel('Speed [rpm]')
% grid
% 
% figure
% subplot(2,1,1);hold on
% plot(analog(:,7)*Km)
% for i=1:length(DnT)
% plot([DnT(i) DnT(i)],[-10 10],'k')
% plot([DnT(i)+Npoint(i) DnT(i)+Npoint(i)],[-20 20],'k')
% end
% ylabel('Vab [V]')
% grid
% for i=1:length(DnT)
% subplot(2,4,4+i);hold on
% plot(analog(DnT(i):DnT(i)+Npoint(i),7)*Km)
% end
% % ylabel('Speed [rpm]')
% grid
% 
% figure
% plot(Power)
% 
% 
% %%
% 
% Win = [10 11]*10^6;
% 
% figure
% hold on
% plot(analog.PhaseCCurrent)
% plot([Win(1) Win(1)],[-15 15],'k')
% plot([Win(2) Win(2)],[-15 15],'k')
% grid
% 
% %%
% speed = 10000;
% p = 5 ;
% Freq = speed*p/60;
% T = 1/Freq ;
% 
% Kfac = 10 ;
% 
% Sampling = 0.64E-6;
% 
% npoint = T/Sampling ;
% 
% IDC = analog.DCCurrent(1:npoint)*Kfac ; 
% 
% IphA = analog.PhaseACurrent(1:npoint)*Kfac ; 
% IphB = analog.PhaseBCurrent(1:npoint)*Kfac ; 
% IphC = analog.PhaseCCurrent(1:npoint) *Kfac; 
% 
% IphSum = (IphA+IphB+IphC)*Kfac;
% 
% VphAC = analog.ACVoltage(1:npoint)*Kfac ; 
% VphAB = analog.ABVoltaage(1:npoint)*Kfac ; 
% VphBC = analog.BCVoltage(1:npoint)*Kfac ; 
% 
% VphSum = (VphAC+VphAB+VphBC)*Kfac ;
% 
% P = VphAC.*IphA+VphAB.*IphB+VphBC.*IphC ;
% Pactive = mean(P) ;
% 
% Time = linspace(0,T,npoint)*1000;
% Har  = linspace(1,936,936)*Freq/1000 ;
% 
% [AmpIDC,~,~] = FFT(IDC,1) ;
% [AmpIa,~,~] = FFT(IphA,1) ;
% [AmpIV,~,~] = FFT(VphAC,1) ;
% 
% figure
% subplot(2,1,1);hold on
% plot(Time,IphA)
% plot(Time,IphB)
% plot(Time,IphC)
% xlabel('Time [msec]');ylabel('Phase current [A]')
% set(gca,'FontName','Times New Roman','fontsize',10)
% grid
% subplot(2,1,2)
% bar(Har,AmpIa)
% xlim([0 60])
% xlabel('Harmonics [kHz]');ylabel('Amplitude [A]')
% set(gca,'FontName','Times New Roman','fontsize',10)
% grid
% 
% figure
% subplot(2,1,1);hold on
% plot(Time,VphAC)
% plot(Time,VphAB)
% plot(Time,VphBC)
% xlabel('Time [msec]');ylabel('Line to line voltage [V]')
% set(gca,'FontName','Times New Roman','fontsize',10)
% grid
% subplot(2,1,2)
% bar(Har,AmpIV)
% xlim([0 60])
% xlabel('Harmonics [kHz]');ylabel('Amplitude [V]')
% set(gca,'FontName','Times New Roman','fontsize',10)
% grid
% 
% figure
% subplot(2,1,1);hold on
% plot(Time,IDC)
% xlabel('Time [msec]');ylabel('DC current [A]')
% set(gca,'FontName','Times New Roman','fontsize',10)
% grid
% subplot(2,1,2)
% bar(Har,AmpIDC)
% xlim([0 60])
% xlabel('Harmonics [kHz]');ylabel('Amplitude [A]')
% set(gca,'FontName','Times New Roman','fontsize',10)
% grid
% 
% figure
% subplot(2,1,1);hold on
% plot(Time,IphSum)
% xlabel('Time [msec]');ylabel('CMM current [A]')
% set(gca,'FontName','Times New Roman','fontsize',10)
% grid
% subplot(2,1,2)
% plot(Time,VphSum)
% xlabel('Time [msec]');ylabel('CMM voltage [V]')
% set(gca,'FontName','Times New Roman','fontsize',10)
% grid
% 
% figure
% subplot(2,1,1);hold on
% plot(Time,P)
% plot([Time(1) Time(end)],[Pactive Pactive])
% xlabel('Time [msec]');ylabel('Power [W]')
% set(gca,'FontName','Times New Roman','fontsize',10)
% grid

