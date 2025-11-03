% OLS.m  -- Least Squares procedure
%     output: N=number of observations
%             K=number of regressors 
%             beta=OLS coefficients
%     input : y=dependent variable (vector)
%             X=regressors (matrix)

function [N,K,beta] = ols(y,X)

if X(:,1) ~= 1 
    disp 'No constant term in regression'; 
end

[N K] = size(X); 

xxinv = inv(X'*X);
beta  = xxinv*X'*y; % OLS coefficients

% You may start adding your codes by filling in "(  ?  )"
% residual = (  ?  );
% dof = N-K; degree of freedom
% sigma2 = (   ?   ); sigma squared
% stdest=sqrt(sigma2); standard deviations
% vcv = (   ?   ); variance matrix
% se = sqrt(diag(vcv)); standard errors


end
