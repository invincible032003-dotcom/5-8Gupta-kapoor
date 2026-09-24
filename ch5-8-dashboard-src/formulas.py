"""Formula & shortcut sheets shown in the dashboard (one list entry per card).

HTML is trusted author content; math goes inside $...$ / $$...$$ and is rendered
with KaTeX at runtime.  verify.py renders every math segment here too.
"""

SECTIONS = [
# ------------------------------------------------------------------ Chapter 5
{"ch": 5, "title": "Distribution function toolkit", "html": r"""
<ul>
<li>$F(x)=P(X\le x)$ is non-decreasing, right-continuous, $F(-\infty)=0$, $F(\infty)=1$; at most countably many jumps.</li>
<li>Jump at $a$: $P(X=a)=F(a)-F(a-0)$. A formula that starts at a non-zero value signals an atom.</li>
</ul>
<table><thead><tr><th>Event</th><th>Probability</th></tr></thead><tbody>
<tr><td>$a<X\le b$</td><td>$F(b)-F(a)$</td></tr>
<tr><td>$a\le X\le b$</td><td>$F(b)-F(a-0)$</td></tr>
<tr><td>$a<X<b$</td><td>$F(b-0)-F(a)$</td></tr>
<tr><td>$a\le X<b$</td><td>$F(b-0)-F(a-0)$</td></tr>
</tbody></table>
<p><b>Shortcut:</b> included left end $\Rightarrow F(a-0)$; excluded right end $\Rightarrow F(b-0)$. For continuous $X$ all four coincide and $P[a\le F(X)\le b]=b-a$.</p>
"""},
{"ch": 5, "title": "Measures from a density", "html": r"""
<table><thead><tr><th>Measure</th><th>Condition / formula</th></tr></thead><tbody>
<tr><td>Mean</td><td>$\int xf(x)\,dx$; for $X\ge0$: $\int_0^\infty[1-F(x)]dx$</td></tr>
<tr><td>Median $M$</td><td>$F(M)=\tfrac12$ — minimises $E|X-c|$</td></tr>
<tr><td>Mode</td><td>$f'(x)=0,\ f''(x)<0$ (or an end point if $f$ is monotone)</td></tr>
<tr><td>Quartiles</td><td>$F(Q_1)=\tfrac14,\ F(Q_3)=\tfrac34$; symmetric about $c$: $Q_1+Q_3=2c$</td></tr>
<tr><td>Harmonic mean</td><td>$H=1/E(1/X)$; Gamma$(\lambda)$: $\lambda-1$; Beta$(m,n)$: $\tfrac{m-1}{m+n-1}$</td></tr>
<tr><td>Skewness / kurtosis</td><td>$\beta_1=\mu_3^2/\mu_2^3$ (sign from $\mu_3$), $\beta_2=\mu_4/\mu_2^2$</td></tr>
</tbody></table>
<p>$\mu_2=\mu_2'-\mu_1'^2,\quad\mu_3=\mu_3'-3\mu_1'\mu_2'+2\mu_1'^3,\quad\mu_4=\mu_4'-4\mu_1'\mu_3'+6\mu_1'^2\mu_2'-3\mu_1'^4$.</p>
<p><b>Triangular</b> law on $[\alpha,\beta]$ with mode $c$: mean $\tfrac{\alpha+\beta+c}3$, variance $\tfrac{\alpha^2+\beta^2+c^2-\alpha\beta-\beta c-c\alpha}{18}$; symmetric of half-width $a$: $a^2/6$.</p>
"""},
{"ch": 5, "title": "Joint, marginal, conditional", "html": r"""
<ul>
<li>Marginal: $f_X(x)=\int f(x,y)\,dy$. Conditional: $f(y\mid x)=f(x,y)/f_X(x)$.</li>
<li>Independence $\iff f(x,y)=f_X(x)f_Y(y)$ for all $(x,y)$. A non-rectangular support (e.g. $0<x<y<1$) already rules it out.</li>
<li>$2\times2$ table: independent $\iff p_{00}p_{11}=p_{01}p_{10}$.</li>
<li>Uniform joint density $\Rightarrow$ every conditional is uniform on its slice.</li>
<li>$f(x,y)=\tfrac14(1+xy)$ on $(-1,1)^2$: $X,Y$ dependent (Cov $=\tfrac19$) but $X^2,Y^2$ independent.</li>
<li>Poisson thinning: $Y\sim P(\lambda)$, $X\mid Y\sim B(Y,p)\Rightarrow X\sim P(\lambda p)$, $Y-X\sim P(\lambda q)$, independent.</li>
<li>Poisson mixed over Exp($\lambda$) rate $\Rightarrow$ Geometric $p=\tfrac\lambda{1+\lambda}$; over Gamma$(r)$ $\Rightarrow$ NB.</li>
</ul>
"""},
{"ch": 5, "title": "Transformations: one and two variables", "html": r"""
<ul>
<li>Monotone $y=g(x)$: $h(y)=f(x)\left|\dfrac{dx}{dy}\right|$ (Theorem 5·9).</li>
<li>$Y=X^2$: $g(y)=\dfrac{f(\sqrt y)+f(-\sqrt y)}{2\sqrt y}$ — count only roots inside the support.</li>
<li>$Y=a+bX$: $g(y)=\dfrac1{|b|}f\left(\dfrac{y-a}b\right)$.</li>
<li>Two variables: $g(u,v)=f(x,y)\,|J|$, $J=\dfrac{\partial(x,y)}{\partial(u,v)}$.</li>
</ul>
<table><thead><tr><th>Target</th><th>Density</th></tr></thead><tbody>
<tr><td>$X+Y$</td><td>$\int f_X(v)f_Y(u-v)\,dv$</td></tr>
<tr><td>$X-Y$</td><td>$\int f_X(u+v)f_Y(v)\,dv$</td></tr>
<tr><td>$XY$</td><td>$\int f_X(v)f_Y(u/v)\,\tfrac1{|v|}dv$</td></tr>
<tr><td>$X/Y$</td><td>$\int |v|\,f_X(uv)f_Y(v)\,dv$</td></tr>
</tbody></table>
<table><thead><tr><th>Standard result</th><th>Law</th></tr></thead><tbody>
<tr><td>$F(X)$; $-\ln U$; $-2\ln U$; $F^{-1}(U)$</td><td>$U(0,1)$; Exp(1); $\chi^2_2$; $F$</td></tr>
<tr><td>$\tan\Theta$, $\Theta\sim U(-\frac\pi2,\frac\pi2)$</td><td>standard Cauchy</td></tr>
<tr><td>$U_1+U_2$ (i.i.d. $U(0,1)$)</td><td>triangular on $(0,2)$</td></tr>
<tr><td>$U_1U_2$</td><td>$-\ln z$ on $(0,1)$</td></tr>
<tr><td>$X+Y,\ \tfrac X{X+Y}$ (i.i.d. Exp)</td><td>Gamma(2), $U(0,1)$ — independent</td></tr>
<tr><td>$X-Y$ (i.i.d. Exp)</td><td>Laplace</td></tr>
<tr><td>$X/Y$ (i.i.d. $N(0,1)$)</td><td>standard Cauchy</td></tr>
<tr><td>$\sqrt{X^2+Y^2}$ (i.i.d. $N(0,1)$)</td><td>Rayleigh $re^{-r^2/2}$; angle uniform, independent</td></tr>
<tr><td>$f(x,y)=g(x+y)$ on the quadrant</td><td>$Z=X+Y$ has density $z\,g(z)$</td></tr>
</tbody></table>
"""},
# ------------------------------------------------------------------ Chapter 6
{"ch": 6, "title": "Expectation, variance, covariance", "html": r"""
<ul>
<li>$E(X)$ exists iff $E|X|<\infty$. Pareto index $\alpha$: $E(X^r)<\infty\iff r<\alpha$. Moments exist downwards: $E|X|^r<\infty\Rightarrow E|X|^s<\infty$ for $s\le r$.</li>
<li>Tail sums: $E(X)=\sum_{n\ge0}P(X>n)$; $E(X^2)=\sum(2n+1)P(X>n)$; $E[X(X-1)]=2\sum nP(X>n)$.</li>
<li>Loss minimisers: $E(X-c)^2\to$ mean; $E|X-c|\to$ median.</li>
<li>$\text{Var}(\sum a_iX_i)=\sum a_i^2\sigma_i^2+2\sum_{i<j}a_ia_j\sigma_{ij}$; $\text{Cov}(aX+bY,cX+dY)=ac\,\sigma_X^2+bd\,\sigma_Y^2+(ad+bc)\sigma_{XY}$.</li>
<li>Independent $X,Y$: $\text{Var}(XY)=\sigma_1^2\sigma_2^2+\mu_1^2\sigma_2^2+\mu_2^2\sigma_1^2$.</li>
<li>$n$ equicorrelated variables: $\rho\ge-\tfrac1{n-1}$. Uncorrelated $\not\Rightarrow$ independent ($X$ symmetric, $Y=X^2$).</li>
<li>Lottery ($m$ of $n$ tickets): $E(S)=\tfrac{m(n+1)}2$, $\text{Var}(S)=\tfrac{m(n+1)(n-m)}{12}$.</li>
<li>Indicator trick: black balls before first white $=\tfrac b{w+1}$; matching problem: mean = variance = 1.</li>
</ul>
"""},
{"ch": 6, "title": "Conditional expectation", "html": r"""
<ul>
<li>$E(Y)=E[E(Y\mid X)]$; $\text{Var}(Y)=E[\text{Var}(Y\mid X)]+\text{Var}[E(Y\mid X)]$.</li>
<li>Random sum $S=\sum_{i=1}^NX_i$: $E(S)=E(N)\mu$, $\text{Var}(S)=E(N)\sigma^2+\text{Var}(N)\mu^2$; Poisson $N$: $\lambda E(X^2)$.</li>
<li>Best predictor in mean square: $E(Y\mid X)$; best linear predictor: regression line.</li>
<li>Exchangeable: $E(X_1\mid X_1+\cdots+X_n)=\bar X$; $E\left[\tfrac{X}{X+Y}\right]=\tfrac12$ for i.i.d. positive.</li>
</ul>
"""},
{"ch": 6, "title": "Generating functions", "html": r"""
<table><thead><tr><th>Function</th><th>Definition</th><th>Key uses</th></tr></thead><tbody>
<tr><td>m.g.f.</td><td>$M(t)=E(e^{tX})$</td><td>$\mu_r'=M^{(r)}(0)$; $M_{aX+b}(t)=e^{bt}M(at)$; may not exist (Cauchy, log-normal, Pareto)</td></tr>
<tr><td>c.g.f.</td><td>$K(t)=\ln M(t)$</td><td>$\kappa_1=\mu,\ \kappa_2=\mu_2,\ \kappa_3=\mu_3,\ \kappa_4=\mu_4-3\mu_2^2$; additive; $\kappa_r(aX+b)=a^r\kappa_r$ ($r\ge2$)</td></tr>
<tr><td>c.f.</td><td>$\phi(t)=E(e^{itX})$</td><td>always exists; $\phi(0)=1$, $|\phi|\le1$, $\phi(-t)=\overline{\phi(t)}$, uniformly continuous; real $\iff$ symmetric</td></tr>
<tr><td>p.g.f.</td><td>$P(s)=E(s^X)$</td><td>$E(X)=P'(1)$; $\text{Var}=P''(1)+P'(1)-P'(1)^2$; $P^{(r)}(1)$ = factorial moment</td></tr>
</tbody></table>
<ul>
<li>$\sum P(X\le n)s^n=\dfrac{P(s)}{1-s}$, $\sum P(X>n)s^n=\dfrac{1-P(s)}{1-s}$, $P(X\text{ even})=\tfrac12[1+P(-1)]$.</li>
<li>Valid c.f.? $e^{-|t|^\alpha}$ only for $0<\alpha\le2$. $\cos t$ yes; $e^{-t^4},\ \tfrac1{1+t^4},\ \log(1+t)$ no.</li>
<li>Pairs: Laplace $\leftrightarrow\tfrac1{1+t^2}$; Cauchy $\leftrightarrow e^{-|t|}$; $U(-a,a)\leftrightarrow\tfrac{\sin at}{at}$; $X^2$ ($X\sim N(0,1)$) $\leftrightarrow(1-2it)^{-1/2}$; $X_1X_2\leftrightarrow(1+t^2)^{-1/2}$.</li>
<li>$\phi_{X+Y}=\phi_X\phi_Y$ does <b>not</b> imply independence (take $X=Y$ Cauchy). Joint c.f. factorisation does.</li>
<li>Compound Poisson: $\ln M_Y=\lambda(M_X-1)\Rightarrow\kappa_r(Y)=\lambda E(X^r)$.</li>
</ul>
"""},
{"ch": 6, "title": "Inequalities", "html": r"""
<table><thead><tr><th>Inequality</th><th>Statement</th></tr></thead><tbody>
<tr><td>Markov</td><td>$X\ge0$: $P(X\ge a)\le E(X)/a$</td></tr>
<tr><td>Chebychev</td><td>$P(|X-\mu|\ge k\sigma)\le\tfrac1{k^2}$; $P(|X-\mu|<c)\ge1-\tfrac{\sigma^2}{c^2}$</td></tr>
<tr><td>Generalised</td><td>$g\ge0$: $P\{g(X)\ge k\}\le E\,g(X)/k$</td></tr>
<tr><td>Jensen</td><td>convex $g$: $E\,g(X)\ge g(EX)$ ($E X^2\ge(EX)^2$, $E\frac1X\ge\frac1{EX}$)</td></tr>
<tr><td>Cauchy–Schwarz</td><td>$[E(XY)]^2\le E(X^2)E(Y^2)$</td></tr>
<tr><td>Lyapunov</td><td>$(E|X|^r)^{1/r}$ non-decreasing in $r$</td></tr>
</tbody></table>
<ul>
<li>Sample size (Chebychev): $n\ge\dfrac{\sigma^2}{\varepsilon^2(1-P)}$; (CLT): $n\ge(z\sigma/\varepsilon)^2$.</li>
<li>$k$ for coverage $P$: $k=1/\sqrt{1-P}$: $0.75\to2,\ 0.89\to3,\ 0.96\to5,\ 0.99\to10$.</li>
<li>Sharpness: mass $\tfrac1{2k^2}$ at $\mu\pm k\sigma$, rest at $\mu$ attains equality.</li>
</ul>
"""},
{"ch": 6, "title": "Convergence & laws of large numbers", "html": r"""
<p>$L^r\Rightarrow P\Rightarrow D$ and a.s. $\Rightarrow P$. $D\Rightarrow P$ only for a constant limit. Checked only at continuity points of the limit.</p>
<table><thead><tr><th>Sequence</th><th>Behaviour</th></tr></thead><tbody>
<tr><td>independent $X_n\sim$ Bernoulli$(1/n)$</td><td>$\to0$ in $P$ and $L^2$, not a.s. (BC-II)</td></tr>
<tr><td>independent $X_n\sim$ Bernoulli$(1/n^2)$</td><td>$\to0$ a.s. (BC-I)</td></tr>
<tr><td>$X_n=n$ w.p. $1/n$, else 0</td><td>$\to0$ in $P$; $E(X_n)=1$ (no $L^1$ convergence)</td></tr>
</tbody></table>
<ul>
<li><b>Chebychev WLLN:</b> $B_n=\text{Var}(S_n)$, $B_n/n^2\to0$. <b>Markov:</b> same condition without independence. <b>Khinchin:</b> i.i.d. with finite mean. <b>Bernoulli:</b> $S_n/n\xrightarrow{P}p$.</li>
<li><b>Kolmogorov SLLN</b> (i.i.d.): $\bar X_n\to\mu$ a.s. $\iff E|X_1|<\infty$. Cauchy means never settle.</li>
<li>$P(X_k=\pm k^\alpha)=\tfrac12$: WLLN iff $\alpha<\tfrac12$ (compare $n^{2\alpha+1}$ with $n^2$).</li>
<li><b>Borel–Cantelli:</b> $\sum P(A_n)<\infty\Rightarrow P(\limsup A_n)=0$; independent and $\sum=\infty\Rightarrow1$. <b>Kolmogorov 0–1:</b> tail events have probability 0 or 1.</li>
<li><b>Slutsky:</b> $X_n\xrightarrow{d}X,\ Y_n\xrightarrow{P}c\Rightarrow X_n+Y_n\xrightarrow{d}X+c,\ X_nY_n\xrightarrow{d}cX$.</li>
</ul>
"""},
# ------------------------------------------------------------------ Chapter 7
{"ch": 7, "title": "Discrete distributions at a glance", "html": r"""
<table><thead><tr><th>Law</th><th>p.m.f.</th><th>Mean</th><th>Variance</th><th>m.g.f.</th></tr></thead><tbody>
<tr><td>Bernoulli$(p)$</td><td>$p^xq^{1-x}$</td><td>$p$</td><td>$pq$</td><td>$q+pe^t$</td></tr>
<tr><td>$B(n,p)$</td><td>$\binom nxp^xq^{n-x}$</td><td>$np$</td><td>$npq$</td><td>$(q+pe^t)^n$</td></tr>
<tr><td>Poisson$(\lambda)$</td><td>$e^{-\lambda}\lambda^x/x!$</td><td>$\lambda$</td><td>$\lambda$</td><td>$e^{\lambda(e^t-1)}$</td></tr>
<tr><td>Geometric (failures)</td><td>$q^xp,\ x\ge0$</td><td>$q/p$</td><td>$q/p^2$</td><td>$\dfrac p{1-qe^t}$</td></tr>
<tr><td>Geometric (trials)</td><td>$q^{x-1}p,\ x\ge1$</td><td>$1/p$</td><td>$q/p^2$</td><td>$\dfrac{pe^t}{1-qe^t}$</td></tr>
<tr><td>Neg. binomial (failures)</td><td>$\binom{x+r-1}{x}p^rq^x$</td><td>$rq/p$</td><td>$rq/p^2$</td><td>$p^r(1-qe^t)^{-r}$</td></tr>
<tr><td>Hypergeometric</td><td>$\dfrac{\binom Mx\binom{N-M}{n-x}}{\binom Nn}$</td><td>$\dfrac{nM}N$</td><td>$npq\dfrac{N-n}{N-1}$</td><td>—</td></tr>
<tr><td>Discrete uniform $1..n$</td><td>$1/n$</td><td>$\tfrac{n+1}2$</td><td>$\tfrac{n^2-1}{12}$</td><td>$\dfrac{e^t(e^{nt}-1)}{n(e^t-1)}$</td></tr>
</tbody></table>
<p>Dispersion: binomial $\sigma^2<\mu$; Poisson $=$; NB/geometric $>$.</p>
"""},
{"ch": 7, "title": "Binomial & Poisson shortcuts", "html": r"""
<ul>
<li>From mean & variance: $q=\sigma^2/\mu$, $n=\mu/p$. Impossible if $\sigma^2\ge\mu$.</li>
<li>Mode: $(n+1)p$ integer $\Rightarrow$ modes $(n+1)p-1,(n+1)p$; else $\lfloor(n+1)p\rfloor$. Poisson: $\lfloor\lambda\rfloor$ (two modes if $\lambda$ integer).</li>
<li>Binomial: $\beta_1=\dfrac{(q-p)^2}{npq}$, $\beta_2=3+\dfrac{1-6pq}{npq}$; $\kappa_{r+1}=pq\,\dfrac{d\kappa_r}{dp}$; $\mu_{r+1}=pq\left[nr\mu_{r-1}+\dfrac{d\mu_r}{dp}\right]$.</li>
<li>Poisson: all $\kappa_r=\lambda$; $\mu_4=3\lambda^2+\lambda$; $\beta_1=1/\lambda$, $\beta_2=3+1/\lambda$; $\mu_{r+1}=\lambda\left[r\mu_{r-1}+\dfrac{d\mu_r}{d\lambda}\right]$.</li>
<li>Recurrences: $p(x+1)=\dfrac{n-x}{x+1}\dfrac pq\,p(x)$; Poisson $p(x+1)=\dfrac\lambda{x+1}p(x)$.</li>
<li>Factorial moments: binomial $n^{(r)}p^r$; Poisson $\lambda^r$.</li>
<li>$P(X\ge k)=P(Y\le p)$, $Y\sim$ Beta$(k,n-k+1)$.</li>
<li>Additive: $B(n_1,p)+B(n_2,p)=B(n_1+n_2,p)$ (same $p$ only); $P(\lambda_1)+P(\lambda_2)=P(\lambda_1+\lambda_2)$; difference not Poisson.</li>
<li>Conditioning on totals: Poissons $\to$ binomial $B\left(n,\tfrac{\lambda_1}{\lambda_1+\lambda_2}\right)$; binomials $\to$ hypergeometric.</li>
<li>$E\left[\tfrac1{X+1}\right]$: Poisson $\tfrac{1-e^{-\lambda}}\lambda$; binomial $\tfrac{1-q^{n+1}}{(n+1)p}$.</li>
<li>Limits: binomial $\to$ Poisson ($n\to\infty,p\to0,np=\lambda$); NB $\to$ Poisson ($r\to\infty,rq=\lambda$); hypergeometric $\to$ binomial ($N\to\infty$).</li>
<li>Useful values: $e^{-0.2}=0.8187,\ e^{-0.5}=0.6065,\ e^{-0.75}=0.4724,\ e^{-1}=0.3679,\ e^{-1.5}=0.2231,\ e^{-2}=0.1353$.</li>
</ul>
"""},
{"ch": 7, "title": "Geometric, negative binomial, multinomial, PSD", "html": r"""
<ul>
<li>Lack of memory: $P(X\ge m+n\mid X\ge m)=P(X\ge n)$ — geometric is the only such discrete law.</li>
<li>Min of independent geometrics: survival $(q_1q_2)^k$. $P(X=Y)=\dfrac p{1+q}$ for i.i.d.</li>
<li>"$k$-th trial is the $r$-th success": $\binom{k-1}{r-1}p^rq^{k-r}$.</li>
<li>NB from moments: $p=\mu/\sigma^2$, $r=\mu^2/(\sigma^2-\mu)$. Sum of $r$ geometrics. Factor $e^{rt}$ out of an m.g.f. to spot the "trials" version.</li>
<li>Multinomial: marginals $B(n,p_i)$; $\text{Cov}(X_i,X_j)=-np_ip_j$; $\rho=-\sqrt{\dfrac{p_ip_j}{q_iq_j}}$; $X_j\mid X_i=x\sim B\left(n-x,\tfrac{p_j}{1-p_i}\right)$; m.g.f. $(\sum p_ie^{t_i})^n$.</li>
<li>Power series $p(x)=a_x\theta^x/f(\theta)$: $\mu=\theta f'/f$, $\mu_2=\theta\,d\mu/d\theta$, $\kappa_{r+1}=\theta\,d\kappa_r/d\theta$. Members: binomial, Poisson, NB, logarithmic (not hypergeometric).</li>
<li>Logarithmic series: mean $\dfrac{-\theta}{(1-\theta)\ln(1-\theta)}$.</li>
</ul>
"""},
# ------------------------------------------------------------------ Chapter 8
{"ch": 8, "title": "Continuous distributions at a glance", "html": r"""
<table><thead><tr><th>Law</th><th>Density</th><th>Mean</th><th>Variance</th><th>m.g.f. / c.f.</th></tr></thead><tbody>
<tr><td>$U(a,b)$</td><td>$\frac1{b-a}$</td><td>$\frac{a+b}2$</td><td>$\frac{(b-a)^2}{12}$</td><td>$\frac{e^{bt}-e^{at}}{(b-a)t}$</td></tr>
<tr><td>$N(\mu,\sigma^2)$</td><td>$\frac1{\sigma\sqrt{2\pi}}e^{-(x-\mu)^2/2\sigma^2}$</td><td>$\mu$</td><td>$\sigma^2$</td><td>$e^{\mu t+\sigma^2t^2/2}$</td></tr>
<tr><td>Exp (mean $\theta$)</td><td>$\frac1\theta e^{-x/\theta}$</td><td>$\theta$</td><td>$\theta^2$</td><td>$(1-\theta t)^{-1}$</td></tr>
<tr><td>$\gamma(a,\lambda)$</td><td>$\frac{a^\lambda}{\Gamma(\lambda)}e^{-ax}x^{\lambda-1}$</td><td>$\lambda/a$</td><td>$\lambda/a^2$</td><td>$(1-t/a)^{-\lambda}$</td></tr>
<tr><td>$\chi^2_n$</td><td>$\gamma(\tfrac12,\tfrac n2)$</td><td>$n$</td><td>$2n$</td><td>$(1-2t)^{-n/2}$</td></tr>
<tr><td>$\beta_1(m,n)$</td><td>$\frac{x^{m-1}(1-x)^{n-1}}{B(m,n)}$</td><td>$\frac m{m+n}$</td><td>$\frac{mn}{(m+n)^2(m+n+1)}$</td><td>—</td></tr>
<tr><td>$\beta_2(m,n)$</td><td>$\frac{x^{m-1}}{B(m,n)(1+x)^{m+n}}$</td><td>$\frac m{n-1}$</td><td>$\frac{m(m+n-1)}{(n-1)^2(n-2)}$</td><td>—</td></tr>
<tr><td>Laplace</td><td>$\frac1{2\lambda}e^{-|x-\mu|/\lambda}$</td><td>$\mu$</td><td>$2\lambda^2$</td><td>c.f. $\frac{e^{i\mu t}}{1+\lambda^2t^2}$</td></tr>
<tr><td>Cauchy</td><td>$\frac\lambda{\pi[\lambda^2+(x-\mu)^2]}$</td><td>none</td><td>none</td><td>c.f. $e^{i\mu t-\lambda|t|}$</td></tr>
<tr><td>Logistic</td><td>$\frac{e^{-x}}{(1+e^{-x})^2}$</td><td>0</td><td>$\pi^2/3$</td><td>—</td></tr>
<tr><td>Weibull</td><td>$S(x)=e^{-(x/\alpha)^\beta}$</td><td>$\alpha\Gamma(1+\frac1\beta)$</td><td>$\alpha^2[\Gamma(1+\frac2\beta)-\Gamma^2(1+\frac1\beta)]$</td><td>—</td></tr>
<tr><td>Pareto $(\alpha,x_0)$</td><td>$\frac{\alpha x_0^\alpha}{x^{\alpha+1}}$</td><td>$\frac{\alpha x_0}{\alpha-1}$</td><td>$\frac{\alpha x_0^2}{(\alpha-1)^2(\alpha-2)}$</td><td>none</td></tr>
<tr><td>Log-normal</td><td>$\ln X\sim N(\mu,\sigma^2)$</td><td>$e^{\mu+\sigma^2/2}$</td><td>$e^{2\mu+\sigma^2}(e^{\sigma^2}-1)$</td><td>none</td></tr>
</tbody></table>
<p>$\beta_2$ ladder: uniform 1.8 · triangular 2.4 · normal 3 · logistic 4.2 · Laplace 6 · exponential 9. Gamma: $\beta_1=4/\lambda$, $\beta_2=3+6/\lambda$.</p>
"""},
{"ch": 8, "title": "Normal distribution facts", "html": r"""
<ul>
<li>Mean = median = mode; inflexion at $\mu\pm\sigma$; maximum ordinate $\frac1{\sigma\sqrt{2\pi}}$.</li>
<li>$\mu_{2r}=1\cdot3\cdots(2r-1)\sigma^{2r}$: $\mu_4=3\sigma^4$, $\mu_6=15\sigma^6$. MD $=\sigma\sqrt{2/\pi}\approx\tfrac45\sigma$; QD $\approx0.6745\sigma\approx\tfrac23\sigma$; QD : MD : SD $=10:12:15$.</li>
<li>Areas: $\pm1\sigma$ 68.27%, $\pm2\sigma$ 95.45%, $\pm3\sigma$ 99.73%; $\pm1.96\sigma$ 95%, $\pm2.576\sigma$ 99%.</li>
<li>$ke^{-ax^2+bx}$: $\mu=\tfrac b{2a}$, $\sigma^2=\tfrac1{2a}$.</li>
<li>$\text{Var}(X^2)=2\sigma^4+4\mu^2\sigma^2$; $|Z|$: mean $\sqrt{2/\pi}$, variance $1-2/\pi$.</li>
<li>Linear combinations of independent normals are normal: mean $\sum a_i\mu_i$, variance $\sum a_i^2\sigma_i^2$. Cramér: if $X+Y$ normal (independent) then both normal.</li>
<li>Continuity correction: $P(X\ge k)\to k-\tfrac12$; $P(X\le k)\to k+\tfrac12$.</li>
<li>$\chi^2_1$ points $=z^2$: $2.706,\ 3.841,\ 6.635$.</li>
</ul>
"""},
{"ch": 8, "title": "Gamma, beta, exponential, Cauchy relations", "html": r"""
<ul>
<li>$\gamma(\lambda_1)+\gamma(\lambda_2)=\gamma(\lambda_1+\lambda_2)$; $\frac X{X+Y}\sim\beta_1(\lambda_1,\lambda_2)$ (independent of $X+Y$); $\frac XY\sim\beta_2(\lambda_1,\lambda_2)$.</li>
<li>$X\sim\beta_1(m,n)\Rightarrow\frac X{1-X}\sim\beta_2(m,n)$, $1-X\sim\beta_1(n,m)$. Beta mode $\frac{m-1}{m+n-2}$; $E(X^r)=\frac{m^{(r\uparrow)}}{(m+n)^{(r\uparrow)}}$.</li>
<li>$\tfrac12Z^2\sim\gamma(\tfrac12)$; sum of $n$ i.i.d. Exp(mean $\theta$) $\sim$ Gamma($n$, scale $\theta$); $E(1/\chi^2_n)=\frac1{n-2}$; Gamma mode $\frac{\lambda-1}a$; $E(X^r)=\frac{\Gamma(\lambda+r)}{\Gamma(\lambda)}$.</li>
<li>Exponential: memoryless; median $\theta\ln2$; IQR $\theta\ln3$; $\beta_1=4,\beta_2=9$; $\min\sim$ Exp$(\sum\lambda_i)$; $P(X_i\text{ first})=\lambda_i/\sum\lambda_j$; $E(X\mid X>a)=a+\theta$; $[X]\sim$ geometric.</li>
<li>Max of $P(a\le X\le b)$ over rates: substitute $u=e^{-\lambda a}$ and maximise a polynomial ($[a,2a]\Rightarrow\tfrac14$).</li>
<li>Cauchy: no mean; median $\mu$, quartiles $\mu\pm\lambda$; $1/X$ standard Cauchy; sums add scales; mean of $n$ Cauchys is Cauchy; $X/Y$ for i.i.d. normals.</li>
<li>Laplace $=X-Y$ (i.i.d. exponentials). Weibull $=(\text{Exp})^{1/\beta}$, hazard $\frac\beta\alpha(x/\alpha)^{\beta-1}$.</li>
</ul>
"""},
{"ch": 8, "title": "CLT, compound, truncated", "html": r"""
<ul>
<li><b>Lindeberg–Lévy:</b> i.i.d., $0<\sigma^2<\infty$: $\frac{S_n-n\mu}{\sigma\sqrt n}\xrightarrow{d}N(0,1)$. <b>De Moivre–Laplace:</b> binomial case. <b>Liapounoff:</b> $\rho/\sigma\to0$, $\rho^3=\sum E|X_i-\mu_i|^3$, $\sigma^2=\sum\sigma_i^2$.</li>
<li>$e^{-n}\sum_{k\le n}n^k/k!\to\tfrac12$; $P(\chi^2_n\le n)\to\tfrac12$.</li>
<li>Round-off (step $h$): each error variance $h^2/12$. $\sum_{i=1}^{12}U_i-6\approx N(0,1)$.</li>
<li>Compound: Poisson$(\Lambda)$ with $\Lambda\sim$ Gamma $\Rightarrow$ NB; $B(n,P)$ with $P\sim U(0,1)\Rightarrow$ uniform on $\{0,\dots,n\}$.</li>
<li>Truncation renormalises: zero-truncated Poisson mean $\frac\lambda{1-e^{-\lambda}}$; binomial $\frac{np}{1-q^n}$; Exp(1) on $(0,1)$: $\frac{e-2}{e-1}$.</li>
</ul>
"""},
{"ch": 8, "title": "Pearson system & transformations", "html": r"""
<p>$\dfrac1y\dfrac{dy}{dx}=\dfrac{x-a}{b_0+b_1x+b_2x^2}$, $\kappa=\dfrac{\beta_1(\beta_2+3)^2}{4(4\beta_2-3\beta_1)(2\beta_2-3\beta_1-6)}$.</p>
<table><thead><tr><th>Criterion</th><th>Type</th></tr></thead><tbody>
<tr><td>$\kappa<0$</td><td>I (Beta I)</td></tr>
<tr><td>$\kappa=0$, $\beta_2<3$ / $=3$ / $>3$</td><td>II / normal / VII ($t$)</td></tr>
<tr><td>$0<\kappa<1$</td><td>IV</td></tr>
<tr><td>$\kappa=1$</td><td>V</td></tr>
<tr><td>$\kappa>1$</td><td>VI (Beta II / $F$)</td></tr>
<tr><td>$2\beta_2-3\beta_1-6=0$ ($\kappa=\infty$)</td><td>III (gamma)</td></tr>
</tbody></table>
<p>Pearson skewness $=\dfrac{\sqrt{\beta_1}(\beta_2+3)}{2(5\beta_2-6\beta_1-9)}$.</p>
<ul>
<li>Variance stabilisers $g=\int dx/\sigma(x)$: Poisson $\sqrt x$ (var $\tfrac14$); proportion $\sin^{-1}\sqrt p$ (var $\tfrac1{4n}$ rad, $\tfrac{820.7}n$ deg); $\sigma\propto\mu$: $\log x$; correlation: Fisher $z=\tanh^{-1}r$, var $\tfrac1{n-3}$.</li>
</ul>
"""},
{"ch": 8, "title": "Order statistics", "html": r"""
<ul>
<li>$f_{(r)}(x)=\dfrac{n!}{(r-1)!(n-r)!}F^{r-1}(1-F)^{n-r}f$; max $nF^{n-1}f$; min $n(1-F)^{n-1}f$.</li>
<li>$P(X_{(r)}\le x)=P(\text{at least }r\text{ of }n\le x)$ — a binomial tail.</li>
<li>Joint min–max: $n(n-1)[F(y)-F(x)]^{n-2}f(x)f(y)$; uniform range density $n(n-1)w^{n-2}(1-w)$.</li>
<li>$U(0,1)$: $X_{(r)}\sim$ Beta$(r,n-r+1)$, $E=\frac r{n+1}$, $\text{Var}=\frac{r(n-r+1)}{(n+1)^2(n+2)}$; $E(\text{range})=\frac{n-1}{n+1}$; $U(0,\theta)$: $E(X_{(n)})=\frac{n\theta}{n+1}$.</li>
<li>Exponential: $X_{(1)}\sim$ Exp$(n\lambda)$, spacings Exp$((n-j+1)\lambda)$ independent; $E(\max)=H_n/\lambda$.</li>
<li>Normal, $n=2$: $E(\max)=\sigma/\sqrt\pi$, $E|X-Y|=2\sigma/\sqrt\pi$. Median asymptotics $N\left(M,\frac1{4nf(M)^2}\right)$; normal: $\frac{\pi\sigma^2}{2n}$, efficiency $2/\pi$.</li>
<li>$P(X_{(1)}<M<X_{(n)})=1-2^{1-n}$.</li>
</ul>
"""},
]
