clear all; close all; clc

addpath Utility

%----
% Name = 'ARC_P43_32188_takeoff_max400_min80_01_fullRes.csv';
% % Path = 'D:\ARQUIMEA GROUP\Keayvan Keramati - phaseAnalysis\data\raw\TYTO\' ;
% Path = 'C:\Users\amarfoli\ARQUIMEA GROUP\Keayvan Keramati - phaseAnalysis\data\raw\TYTO\' ;
% uiopen(fullfile(Path,Name),1)

% load('P43_32188_max80_min80.mat')
% P43(1).Name='P43-32188-max80-min80';
% P43(1).Tyto=Tyto; clear Tyto
% 
load('P43_32188_max100_min80.mat')
P43(1).Name='P43-32188-max80-min80';
P43(1).Tyto=Tyto; clear Tyto

load('P43_32188_max150_min80.mat')
P43(2).Name='P43-32188-max80-min80';
P43(2).Tyto=Tyto; clear Tyto

load('P43_32188_max200_min80.mat')
P43(3).Name='P43-32188-max80-min80';
P43(3).Tyto=Tyto; clear Tyto

load('P43_32188_max250_min80.mat')
P43(4).Name='P43-32188-max80-min80';
P43(4).Tyto=Tyto; clear Tyto

load('P43_32188_max300_min80.mat')
P43(5).Name='P43-32188-max80-min80';
P43(5).Tyto=Tyto; clear Tyto

load('P43_32188_max350_min80.mat')
P43(6).Name='P43-32188-max80-min80';
P43(6).Tyto=Tyto; clear Tyto

load('P43_32188_max400_min80.mat')
P43(7).Name='P43-32188-max80-min80';
P43(7).Tyto=Tyto; clear Tyto


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
    P43(qq).Time_Torque_tyto = P43(qq).Time_Torque_tyto(~isnan(P43(qq).Tyto(:,7)));
    P43(qq).Speed_tyto = P43(qq).Tyto(:,7) ;
    P43(qq).Speed_tyto = P43(qq).Speed_tyto(~isnan(P43(qq).Tyto(:,7)));

    P43(qq).Idc_tyto = P43(qq).Tyto(:,6) ;
    P43(qq).Vdc_tyto = P43(qq).Tyto(:,5) ;
    P43(qq).Pdc_tyto = P43(qq).Vdc_tyto.*P43(qq).Idc_tyto ;
    P43(qq).Idc_tyto = P43(qq).Idc_tyto(~isnan(P43(qq).Tyto(:,6)));
    P43(qq).Vdc_tyto = P43(qq).Vdc_tyto(~isnan(P43(qq).Tyto(:,5)));
    P43(qq).Pdc_tyto = P43(qq).Pdc_tyto(~isnan(P43(qq).Pdc_tyto));

end

figure
subplot(2,1,1)
hold on
for qq=1:size(P43,2)
plot(P43(qq).Time_Torque_tyto,P43(qq).Speed_tyto,'-','LineWidth',2)
end
xticks(0:0.5:30)
set(gca,'FontName','Times New Roman','fontsize',12)
ylabel('Speed [rpm]')
xlabel('Time [sec]')
grid

subplot(2,1,2)
hold on
for qq=1:size(P43,2)
plot(P43(qq).Time_Torque_tyto,P43(qq).Speed_tyto,'-','LineWidth',2)
end
xlim([19.8 22])
xticks(0:0.1:30)
set(gca,'FontName','Times New Roman','fontsize',12)
ylabel('Speed [rpm]')
xlabel('Time [sec]')
grid
legend('Imax-100A','Imax-150A','Imax-200A','Imax-250A','Imax-300A','Imax-350A','Imax-400A')
sgtitle('Take off test','FontName','Times New Roman','fontsize',18)
