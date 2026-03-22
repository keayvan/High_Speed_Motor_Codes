clear all; close all; clc

addpath Utility

%----
% Name = 'ARC_P43_32188_3phases_selection_steps_01\analog.csv';
% Path = 'D:\ARQUIMEA GROUP\Keayvan Keramati - phaseAnalysis\data\raw\Salea\' ;
% uiopen(fullfile(Path,Name),1)
% 
% Name = 'ARC_P43_32188_3phases_selection_steps_01_fullRes.csv';
% Path = 'D:\ARQUIMEA GROUP\Keayvan Keramati - phaseAnalysis\data\raw\TYTO\' ;
% uiopen(fullfile(Path,Name),1)

load('P43_32193.mat')
P43(1).Name='P43-32193';
P43(1).Salea=Salea; clear Salea
P43(1).Tyto=Tyto; clear Tyto

load('P43_32188.mat')
P43(2).Name='P43-32188';
P43(2).Salea=Salea; clear Salea
P43(2).Tyto=Tyto; clear Tyto


%%
%--- Tyto results
close all;clc

FontS=11;

polepairs=4;

dS=0.5;

DnT = [0.8 1;1.3 1.5;1.8 2;2.3 2.5;2.8 3]*10^4 ;
DnS = [0.1 0.1+dS;1 1+dS;1.9 1.9+dS;2.9 2.9+dS;4 4+dS]*10^3 ;

for qq=1:size(P43,2)

    P43(qq).Torque_tyto = P43(qq).Tyto(:,4) ;
    P43(qq).Torque_tyto = P43(qq).Torque_tyto(~isnan(P43(qq).Tyto(:,4)));
    P43(qq).Time_Torque_tyto = P43(qq).Tyto(:,1) ;
    P43(qq).Time_Torque_tyto = P43(qq).Time_Torque_tyto(~isnan(P43(qq).Tyto(:,4)));
    P43(qq).Speed_tyto = P43(qq).Tyto(:,7) ;
    P43(qq).Speed_tyto = P43(qq).Speed_tyto(~isnan(P43(qq).Tyto(:,7)));

    P43(qq).Idc_tyto = P43(qq).Tyto(:,6) ;
    P43(qq).Vdc_tyto = P43(qq).Tyto(:,5) ;
    P43(qq).Pdc_tyto = P43(qq).Vdc_tyto.*P43(qq).Idc_tyto ;
    P43(qq).Idc_tyto = P43(qq).Idc_tyto(~isnan(P43(qq).Tyto(:,6)));
    P43(qq).Vdc_tyto = P43(qq).Vdc_tyto(~isnan(P43(qq).Tyto(:,5)));
    P43(qq).Pdc_tyto = P43(qq).Pdc_tyto(~isnan(P43(qq).Pdc_tyto));

    for i=1:length(DnT)
    P43(qq).Torque_mean(i)   = mean(P43(qq).Torque_tyto(DnT(i,1):DnT(i,2))) ;
    P43(qq).Speed_mean(i)    = mean(P43(qq).Speed_tyto(DnS(i,1):DnS(i,2))) ;
    P43(qq).Idc_mean_tyto(i) = mean(P43(qq).Idc_tyto(DnT(i,1):DnT(i,2))) ;
    P43(qq).Vdc_mean_tyto(i) = mean(P43(qq).Vdc_tyto(DnT(i,1):DnT(i,2))) ;
    P43(qq).Power_Mech(i)    = P43(qq).Torque_mean(i)*P43(qq).Speed_mean(i)*2*pi/60 ;
    P43(qq).Pdc_mean_tyto(i) = P43(qq).Idc_mean_tyto(i)*P43(qq).Vdc_mean_tyto(i) ;
    end 

    P43(qq).Freq = P43(qq).Speed_mean*polepairs/60 ;
    P43(qq).Period = 1./P43(qq).Freq ;
    P43(qq).Eff_drive_tyto = (P43(qq).Power_Mech./P43(qq).Pdc_mean_tyto)*100 ;

end


for qq=1:size(P43,2)

figure
subplot(2,2,1);hold on
plot(P43(qq).Torque_tyto)
for i=1:length(DnT)
plot([DnT(i,1) DnT(i,1)],[-1 1],'k')
plot([DnT(i,2) DnT(i,2)],[-1 1],'k')
end
ylabel('Torque [Nm]');xlabel('Samples')
set(gca,'FontName','Times New Roman','fontsize',FontS)
grid
subplot(2,2,2);hold on
plot(P43(qq).Speed_tyto)
for i=1:length(DnT)
plot([DnS(i,1) DnS(i,1)],[-1 15000],'k')
plot([DnS(i,2) DnS(i,2)],[-1 15000],'k')
end
ylabel('Speed [rpm]');xlabel('Samples')
set(gca,'FontName','Times New Roman','fontsize',FontS)
grid
subplot(2,2,3);hold on
plot(P43(qq).Idc_tyto)
for i=1:length(DnT)
plot([DnT(i,1) DnT(i,1)],[-1 100],'k')
plot([DnT(i,2) DnT(i,2)],[-1 100],'k')
end
ylabel('Idc [A]');xlabel('Samples')
set(gca,'FontName','Times New Roman','fontsize',FontS)
grid
subplot(2,2,4);hold on
plot(P43(qq).Pdc_tyto)
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
for i=1:size(P43,2)
subplot(3,4,i)
bar(P43(i).Speed_mean/1000,P43(i).Eff_drive_tyto)
xticks(round(P43(i).Speed_mean)/1000)
set(gca,'FontName','Times New Roman','fontsize',10)
ylabel('Eff [%]')
xlabel('Speed [krpm]')
ylim([30 100])
grid
t=title(P43(i).Name);
set(t,'Units','normalized')
set(t, 'Position', [0.2 1.05 0])
% h=legend('Power train tyto','FontName','Times New Roman','fontsize',10,'Orientation','horizontal');
% set(h, 'Units','normalized', 'Position',[0.5 0.94 0.1 0.05]);
end




%%

Km = 10 ;

DnT = [1 2.7 4 5.5 7.5]*10^7 ;

for qq=1:size(P43,2)

    P43(qq).Vab_salea =  P43(qq).Salea(:,8)*Km ;
    P43(qq).Vbc_salea =  P43(qq).Salea(:,9)*Km ;
    P43(qq).Vca_salea =  P43(qq).Salea(:,7)*Km ;
    
    P43(qq).Va_salea = 1/3*(P43(qq).Vab_salea-P43(qq).Vca_salea) ;
    P43(qq).Vb_salea = 1/3*(P43(qq).Vbc_salea-P43(qq).Vab_salea) ;
    P43(qq).Vc_salea = 1/3*(P43(qq).Vca_salea-P43(qq).Vbc_salea) ;
    
    P43(qq).Ia_salea =  P43(qq).Salea(:,4)*Km ;
    P43(qq).Ib_salea =  P43(qq).Salea(:,3)*Km ;
    P43(qq).Ic_salea =  P43(qq).Salea(:,2)*Km ;
    
    % Power = Vab.*Ia+Vbc.*Ib+Vca.*Ic ;
    
    P43(qq).Pac_salea = P43(qq).Va_salea.*P43(qq).Ia_salea+P43(qq).Vb_salea.*P43(qq).Ib_salea+P43(qq).Vc_salea.*P43(qq).Ic_salea ;
    P43(qq).Vdc_salea = P43(qq).Salea(:,6)*Km ;
    P43(qq).Idc_salea = -P43(qq).Salea(:,5)*Km ;
    P43(qq).Pdc_salea = P43(qq).Vdc_salea.*P43(qq).Idc_salea ;
    
    NPeriod = 1 ;
    
    clear DCcut Vcut Icut Pcut
    for i=1:length(DnT)
    
    Period_sampling = 6.4*10^-7/2 ;
    P43(qq).Npoint = round(P43(qq).Period./Period_sampling) ;
    
    P43(qq).cut(i).Vdc_salea = P43(qq).Vdc_salea(DnT(i):DnT(i)+P43(qq).Npoint(i)*NPeriod) ;
    P43(qq).cut(i).Idc_salea = P43(qq).Idc_salea(DnT(i):DnT(i)+P43(qq).Npoint(i)*NPeriod) ;
    
    P43(qq).cut(i).Va_salea = P43(qq).Va_salea(DnT(i):DnT(i)+P43(qq).Npoint(i)*NPeriod) ;
    P43(qq).cut(i).Vb_salea = P43(qq).Vb_salea(DnT(i):DnT(i)+P43(qq).Npoint(i)*NPeriod) ;
    P43(qq).cut(i).Vc_salea = P43(qq).Vc_salea(DnT(i):DnT(i)+P43(qq).Npoint(i)*NPeriod) ;

    P43(qq).cut(i).Ia_salea = P43(qq).Ia_salea(DnT(i):DnT(i)+P43(qq).Npoint(i)*NPeriod) ;
    P43(qq).cut(i).Ib_salea = P43(qq).Ib_salea(DnT(i):DnT(i)+P43(qq).Npoint(i)*NPeriod) ;
    P43(qq).cut(i).Ic_salea = P43(qq).Ic_salea(DnT(i):DnT(i)+P43(qq).Npoint(i)*NPeriod) ;

    P43(qq).Vdc_mean_salea(i)= mean(P43(qq).cut(i).Vdc_salea) ;
    P43(qq).Idc_mean_salea(i) =mean(P43(qq).cut(i).Idc_salea) ;
    
    P43(qq).Va_rms_salea(i) = sqrt(1/length(P43(qq).cut(i).Va_salea)*sum(P43(qq).cut(i).Va_salea.^2)) ;
    P43(qq).Vb_rms_salea(i) = sqrt(1/length(P43(qq).cut(i).Vb_salea)*sum(P43(qq).cut(i).Vb_salea.^2)) ;
    P43(qq).Vc_rms_salea(i) = sqrt(1/length(P43(qq).cut(i).Vc_salea)*sum(P43(qq).cut(i).Vc_salea.^2)) ;
    
    P43(qq).Ia_rms_salea(i) = sqrt(1/length(P43(qq).cut(i).Ia_salea)*sum(P43(qq).cut(i).Ia_salea.^2)) ;
    P43(qq).Ib_rms_salea(i) = sqrt(1/length(P43(qq).cut(i).Ib_salea)*sum(P43(qq).cut(i).Ib_salea.^2)) ;
    P43(qq).Ic_rms_salea(i) = sqrt(1/length(P43(qq).cut(i).Ic_salea)*sum(P43(qq).cut(i).Ic_salea.^2)) ;
    
    [P43(qq).fft(i).AmpVa,P43(qq).fft(i).AngVa,P43(qq).fft(i).FunVa] = FFT(P43(qq).cut(i).Va_salea,NPeriod) ;
    [P43(qq).fft(i).AmpVb,P43(qq).fft(i).AngVb,P43(qq).fft(i).FunVb] = FFT(P43(qq).cut(i).Vb_salea,NPeriod) ;
    [P43(qq).fft(i).AmpVc,P43(qq).fft(i).AngVc,P43(qq).fft(i).FunVc] = FFT(P43(qq).cut(i).Vc_salea,NPeriod) ;
    
    [P43(qq).fft(i).AmpIa,P43(qq).fft(i).AngIa,P43(qq).fft(i).FunIa] = FFT(P43(qq).cut(i).Ia_salea,NPeriod) ;
    [P43(qq).fft(i).AmpIb,P43(qq).fft(i).AngIb,P43(qq).fft(i).FunIb] = FFT(P43(qq).cut(i).Ib_salea,NPeriod) ;
    [P43(qq).fft(i).AmpIc,P43(qq).fft(i).AngIc,P43(qq).fft(i).FunIc] = FFT(P43(qq).cut(i).Ic_salea,NPeriod) ;
    
    P43(qq).PFa(i) = cos(P43(qq).fft(i).AngVa(NPeriod)-P43(qq).fft(i).AngIa(NPeriod));
    P43(qq).PFb(i) = cos(P43(qq).fft(i).AngVb(NPeriod)-P43(qq).fft(i).AngIb(NPeriod));
    P43(qq).PFc(i) = cos(P43(qq).fft(i).AngVc(NPeriod)-P43(qq).fft(i).AngIc(NPeriod));
    
    % Pcut(i).Power    = Power(DnT(i):DnT(i)+Npoint(i)*NPeriod) ;
    P43(qq).cut(i).Pac_salea    = P43(qq).Pac_salea(DnT(i):DnT(i)+P43(qq).Npoint(i)*NPeriod) ;
    P43(qq).cut(i).Pac_fh_salea = P43(qq).fft(i).FunVa.*P43(qq).fft(i).FunIa+P43(qq).fft(i).FunVb.*P43(qq).fft(i).FunIb+P43(qq).fft(i).FunVc.*P43(qq).fft(i).FunIc  ;
    P43(qq).cut(i).Pdc_salea   = P43(qq).Pdc_salea(DnT(i):DnT(i)+P43(qq).Npoint(i)*NPeriod) ;
    
    % Pcut(i).AC_power_mean = mean(Pcut(i).Power) ;
    P43(qq).Pac_mean_salea(i) = mean(P43(qq).cut(i).Pac_salea) ;
    P43(qq).Pac_fh_mean_salea(i) = mean(P43(qq).cut(i).Pac_fh_salea) ;
    P43(qq).Pdc_mean_salea(i) = mean(P43(qq).cut(i).Pdc_salea) ;
    % Pcut(i).Electronic_losses = Pcut(i).DC_power_mean - Pcut(i).AC_power_mean;
    
    % P43(qq).Pcut(i).DC_rms = P43(qq).DCcut(i).Vdcrms*P43(qq).DCcut(i).Idcrms;
    % P43(qq).Pcut(i).AC_rms = P43(qq).cut(i).Va_salearms*P43(qq).cut(i).Ia_salearms+P43(qq).cut(i).Vb_salearms*P43(qq).cut(i).Ib_salearms+P43(qq).cut(i).Vc_salearms*P43(qq).cut(i).Ic_salearms;
    % P43(qq).Pcut(i).Electronic_losses_rms = P43(qq).Pcut(i).DC_rms - P43(qq).Pcut(i).AC_rms ;
    
    end

    P43(qq).Eff_drive_salea = (P43(qq).Power_Mech./P43(qq).Pdc_mean_salea)*100 ;
    P43(qq).Eff_motor = (P43(qq).Power_Mech./P43(qq).Pac_mean_salea)*100 ;
    P43(qq).Eff_electronic = (P43(qq).Pac_mean_salea./P43(qq).Pdc_mean_salea)*100 ;

end




for qq=1:size(P43,2)

    figure
    hold on
    plot( P43(qq).Idc_salea)
    for i=1:length(DnT)
    plot([DnT(i) DnT(i)],[-50 100],'k')
    % plot([DnT(i)+MGM(qq).Npoint(i)*NPeriod DnT(i)+MGM(qq).Npoint(i)*NPeriod],[-50 100],'k')
    end
    ylabel('Vdc [V]');xlabel('Samples');%ylim([15 20])
    set(gca,'FontName','Times New Roman','fontsize',FontS)
    grid
    
    % sgtitle('Salea mesurements MGM','FontName','Times New Roman','fontsize',FontS+2)

end


for qq=1:size(P43,2)

    figure
    subplot(2,2,[1 2])
    bar(P43(qq).Speed_mean/1000,[P43(qq).Eff_drive_tyto; P43(qq).Eff_drive_salea])
    xticks(round(P43(qq).Speed_mean)/1000)
    set(gca,'FontName','Times New Roman','fontsize',10)
    ylabel('Eff [%]')
    xlabel('Speed [krpm]')
    ylim([30 100])
    legend('tyto','salea')
    grid
    t=title(P43(qq).Name);
    set(t,'Units','normalized')
    set(t, 'Position', [0.07 1 0])
    subplot(2,2,3)
    bar(P43(qq).Speed_mean/1000,[P43(qq).Idc_mean_tyto; P43(qq).Idc_mean_salea])
    xticks(round(P43(qq).Speed_mean)/1000)
    set(gca,'FontName','Times New Roman','fontsize',10)
    ylabel('Idc [A]')
    xlabel('Speed [krpm]')
    % ylim([30 100])
    grid
    subplot(2,2,4)
    bar(P43(qq).Speed_mean/1000,[P43(qq).Vdc_mean_tyto; P43(qq).Vdc_mean_salea])
    xticks(round(P43(qq).Speed_mean)/1000)
    set(gca,'FontName','Times New Roman','fontsize',10)
    ylabel('Vdc [V]')
    xlabel('Speed [krpm]')
    % ylim([30 100])
    grid

end


for qq=1:size(P43,2)
    for i=1:length(DnT)

    figure
    subplot(3,3,1);hold on
    plot(P43(qq).cut(i).Va_salea,'b','LineWidth',1.5)
    % plot(cut(i).Va_saleab,'k','LineWidth',1.5)
    % plot(Vcut(i).FunVab,'r','LineWidth',1.5)
    set(gca,'FontName','Times New Roman','fontsize',FontS)
    xlabel('Samples');ylabel('PhA [V]');grid

    subplot(3,3,2);hold on
    plot(P43(qq).cut(i).Vb_salea,'b','LineWidth',1.5)
    % plot(Vcut(i).FunVbc,'r','LineWidth',1.5)
    set(gca,'FontName','Times New Roman','fontsize',FontS)
    xlabel('Samples');ylabel('PhB [V]');grid

    subplot(3,3,3);hold on
    plot(P43(qq).cut(i).Vc_salea,'b','LineWidth',1.5)
    % plot(Vcut(i).FunVca,'r','LineWidth',1.5)
    set(gca,'FontName','Times New Roman','fontsize',FontS)
    xlabel('Samples');ylabel('PhC [V]');grid

    subplot(3,3,4);hold on
    plot(P43(qq).cut(i).Ia_salea,'b','LineWidth',1.5)
    % plot(Icut(i).FunIa,'r','LineWidth',1.5)
    set(gca,'FontName','Times New Roman','fontsize',FontS)
    xlabel('Samples');ylabel('PhA [A]');grid

    subplot(3,3,5);hold on
    plot(P43(qq).cut(i).Ib_salea,'b','LineWidth',1.5)
    % plot(Icut(i).FunIb,'r','LineWidth',1.5)
    set(gca,'FontName','Times New Roman','fontsize',FontS)
    xlabel('Samples');ylabel('PhB [A]');grid

    subplot(3,3,6);hold on
    plot(P43(qq).cut(i).Ic_salea,'b','LineWidth',1.5)
    % plot(Icut(i).FunIc,'r','LineWidth',1.5)
    set(gca,'FontName','Times New Roman','fontsize',FontS)
    set(gca,'FontName','Times New Roman','fontsize',FontS)
    xlabel('Samples');ylabel('PhC [A]');grid

    subplot(3,3,[7 9]);hold on
    plot(P43(qq).cut(i).Pac_salea,'b','LineWidth',1.5)
    plot([0 size(P43(qq).Pac_mean_salea(i),1)],[P43(qq).Pac_mean_salea(i) P43(qq).Pac_mean_salea(i)],'g','LineWidth',1.5)
    plot(P43(qq).cut(i).Pdc_salea,'r','LineWidth',1.5)
    set(gca,'FontName','Times New Roman','fontsize',FontS)
    set(gca,'FontName','Times New Roman','fontsize',FontS)
    xlabel('Samples');ylabel('Power [W]');grid

    end
end


%%


close all
for qq=1:size(P43,2)
    for i=1:2%length(DnT)
    
    figure
    subplot(2,2,1)
    plot(P43(qq).cut(i).Ia_salea,'b','LineWidth',1.5)
    set(gca,'FontName','Times New Roman','fontsize',FontS)
    xlabel('Samples');ylabel('PhA [A]');grid
    subplot(2,2,2)
    plot(P43(qq).cut(i).Va_salea,'b','LineWidth',1.5)
    set(gca,'FontName','Times New Roman','fontsize',FontS)
    xlabel('Samples');ylabel('PhA [V]');grid
    subplot(2,2,3)
    b=bar(P43(qq).Freq(i)*[1:size(P43(qq).fft(i).AmpIa,1)]/1000,P43(qq).fft(i).AmpIa);
    xlabel('Harmonic order');ylabel('Amplitude [A]');grid
    set(gca,'FontName','Times New Roman','fontsize',FontS)
    xlim([P43(qq).Freq(i)-10 P43(qq).Freq(i)*20]/1000)
    grid
    subplot(2,2,4)
    b=bar(P43(qq).Freq(i)*[1:size(P43(qq).fft(i).AmpIa,1)]/1000,P43(qq).fft(i).AmpVa);
    xlabel('Harmonic order');ylabel('Amplitude [V]');grid
    set(gca,'FontName','Times New Roman','fontsize',FontS)
    xlim([P43(qq).Freq(i)-10 P43(qq).Freq(i)*20]/1000)
    grid

    end
end

for qq=1:size(P43,2)
    for i=1:2%length(DnT)
    
    figure
    subplot(2,1,1)
    plot(P43(qq).cut(i).Ia_salea,'b','LineWidth',1.5)
    set(gca,'FontName','Times New Roman','fontsize',FontS)
    xlabel('Samples');ylabel('PhA [A]');grid
    subplot(2,1,2)
    b=bar(P43(qq).fft(i).AmpIa);
    xlabel('Harmonic order');ylabel('Amplitude [A]');grid
    set(gca,'FontName','Times New Roman','fontsize',FontS)
    xlim([0 80])
    grid


    % subplot(2,2,2)
    % plot(P43(qq).cut(i).Va_salea,'b','LineWidth',1.5)
    % set(gca,'FontName','Times New Roman','fontsize',FontS)
    % xlabel('Samples');ylabel('PhA [V]');grid
    % 
    % subplot(2,2,4)
    % b=bar(P43(qq).fft(i).AmpVa);
    % xlabel('Harmonic order');ylabel('Amplitude [V]');grid
    % set(gca,'FontName','Times New Roman','fontsize',FontS)
    % xlim([0 60])
    % grid

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
for qq=1:size(P43,2)
subplot(2,1,qq)
bar(P43(qq).Speed_mean,[P43(qq).Eff_drive_salea; P43(qq).Eff_drive_tyto ;P43(qq).Eff_motor; P43(qq).Eff_electronic])
xticks(round(P43(qq).Speed_mean))
set(gca,'FontName','Times New Roman','fontsize',12)
ylabel('Eff [%]')
xlabel('Speed [rpm]')
ylim([30 100])
grid
t=title(P43(qq).Name);
set(t,'Units','normalized')
set(t, 'Position', [0.07 1 0])
end
h=legend('Power train','Power train tyto','Motor','Electronic','FontName','Times New Roman','fontsize',12,'Orientation','horizontal');
set(h, 'Units','normalized', 'Position',[0.5 0.93 0.1 0.05]);


figure
for qq=1:size(ARC,2)
subplot(2,1,qq)
bar(ARC(qq).Speed_mean,[ARC(qq).Eff_drive; ARC(qq).Eff_motor; ARC(qq).Eff_electronic])
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




