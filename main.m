clear all;
close all;
 
load( 'nerlove.mat'); % 'nerlove.mat' contains a matrix named 'rawData', which has the same data as 'nerlove.asc'
 
n=size(rawData, 1); % number of rows in rawData
y=log(rawData(:, 1)); % The first column contains your y (dependent variable) before taking logs
X=[ones(n, 1) log(rawData(:, 2:end))]; % X is your data matrix for regressors including the constant term 

[n,K,beta]=ols(y, X);
disp 'OLS coefficients'
disp(beta); % print OLS coefficients