Model We are asked to find the magnetic field due to a simple current distribution, so this example is a typical problem for which the Biot-Savart law is appropriate. We must find the field contribution from a small element of current and then integrate over the current distribution from $ \theta_{1} $ to $ \theta_{2} $ , as shown in Figure 29.3b.

Analyse Let's start by considering a length element $ d \vec{s} $ locateda distance r from P. The direction of the magnetic field at point P due to the current in this element is out of the page because $ d \vec{s} \times\hat{\mathbf{r}} $ is out of thepage.Infact, becauseall thecurr entelements $ I d \vec{\mathbf{s}} $ lie in the plane of the page, they all produce a magnetic field directed out of the page at point P. Therefore, the direction of the magnetic field at point P is out of the page and we need only find the magnitude of the field.We place the origin at O and let point P be along thepositive y axis, with $ \mathrm\; \hat{\bf k} $ being a unit vector pointing out of the page.

From the geometry in Figure 29.3a, we can see that the angle between the vectors $ d \vec{s} $ and $ \mathrm\; \vec{\bf r} $ is $ \left( \frac{\pi} {2}-\theta\right) $ radians.

Evaluate the cross product in the Biot-Savart law:

$$
d \vec{\mathbf{s}} \times\hat{\mathbf{r}}=\left| d \vec{\mathbf{s}} \times\hat{\mathbf{r}} \right| \hat{\mathbf{k}}=\left[ d x \operatorname{s i n} \left( \frac{\pi} {2}-\theta\right) \right] \hat{\mathbf{k}}=( d x \operatorname{c o s} \theta) \hat{\mathbf{k}}
$$

Substitute into Equation 29.1:

$$
d \vec{\mathbf{B}}=( d B ) \hat{\mathbf{k}}=\frac{\mu_{_0} I} {4 \pi} \frac{d x \operatorname{c o s} \theta} {r^{2}} \hat{\mathbf{k}}
$$

(1)

From the geometry in Figure 29.3a, express r in terms of $ \theta: $

$$
r=\frac{a} {\operatorname{c o s} \theta}
$$

(2)

Figure 29.3 (Example 29.1) (a) A thin, straight wire carrying a current I (b) The angles $ \theta_{1} $ and $ \theta_{2} $ are used for determining the net field.

Notice that tan $ \theta=-x / a $ from the right triangle in Figure 29.3a (the negative sign is necessary because $ d \mathbf{\vec{s}} $ is located at a negative value of x ) and solve for x:

$$
x=-a \operatorname{t a n} \theta
$$

Find the differential dx:

$$
d x=-a \operatorname{s e c}^{2} \theta\, d \theta=-\frac{a \, d \theta} {\operatorname{c o s}^{2} \theta}
$$

(3)

Substitute Equations (2) and (3) into the magnitude of the field from Equation (1):

$$
d B=-\frac{\mu_{0} I} {4 \pi} \! \left( \frac{a \, d \theta} {\operatorname{c o s}^{2} \theta} \right) \! \left( \frac{\operatorname{c o s}^{2} \theta} {a^{2}} \right) \! \operatorname{c o s} \theta=-\frac{\mu_{0} I} {4 \pi a} \! \operatorname{c o s} \theta\, d \theta
$$

(4)

Integrate Equation (4) over all length elements on the wire, where the subtending angles range from $ \theta_{1} $ to $ \theta_{2} $ as defined in Figure29.3b:

$$
B=-\frac{\mu_{0} I} {4 \pi a} \int_{\theta_{1}}^{\theta_{2}} \cos\theta d \theta=\frac{\mu_{0} I} {4 \pi a} ( \operatorname{s i n} \theta_{1}-\operatorname{s i n} \theta_{2} )
$$

(29.4)

Check the dimensions, noting that the quantity in brackets is dimensionless:

$$
[ \mathrm{M Q}^{-1} \mathrm{T}^{-1} ]=[ \mathrm{M L Q}^{-2} ] [ \mathrm{Q T}^{-1} ] / [ \mathrm{L} ]=[ \mathrm{M Q}^{-1} \mathrm{T}^{-1} ]
$$

(B) Find an expression for the field at a point near a very long current-carrying wire.

# Solution

We can use Equation 29.4 to find the magnetic field of any straight current-carrying wire if we know the geometry and hence the angles $ \theta_{1} $ and $ \theta_{2} $ If the wire in Figure 29.3b becomes infinitely long, we see that $ \theta_{1}=\pi/ 2 $ and $ \theta_{2}=-\pi/ 2 $ for

CHAPTER 29 MAGNETIC FIELDS

Copyright 2017 Cengage Learning.All Rights Reserved.May not be copied, scanned, or duplicated,in whole or in part. WCN 02-300

Example 29.1 cont.

819
