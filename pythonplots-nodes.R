x = seq(5,50, by=5) # number of nodes


# connected topology:
# success rate, avg time, avg sent bytes, avg received bytes
y0 = c(1.0,0.98,1.0,0.97,1.0,0.99,1.0,1.0,1.0,0.98)
t0 = c(0.01415098,0.03332344,0.05019935,0.07068269,0.09001792,0.11228809,0.1356718,0.15983331,0.17294907,0.20703944)
s0 = c(148.52,361.26,558.99,758.49,950.5,1170.23,1371.02,1565.56,1746.74,1844.58)
r0 = c(176.67,644.57,1321.86,2272.23,3412.06,4848.96,6467.01,8241.01,10253.73,12452.05)

# 90% random topology
y1 = c(0.89,0.6,0.66,0.44,0.55,0.32,0.43,0.34,0.39,0.29)
t1 = c(0.0128958,0.02734136,0.04725522,0.05892445,0.07902156,0.08803739,0.10333648,0.12227073,0.14214576,0.18394787)
s1 = c(158.59,329.57,543.37,650.58,871.21,931.17,1102.74,1285.06,1508.84,1541.05)
r1 = c(159.14,569.66,1195.63,2016.01,3096.34,4360.82,5667.72,7080.03,9530.11,11683.31)


png('success-q90f15r3.png', width=800, height=600, pointsize=18)
plot(x,y0, xlab="number of nodes", ylab="% success", main="Python simulation with 90% quorum, 15% failure rate, 3 retries", ylim=c(0,1), xlim=c(0, 55), pch=0)
points(x,y1, pch=15, col="blue")
#points(x,y3, col="blue", pch=0)

# fit a line to the points
y0.fit <- lm(y0 ~ x)
y1.fit <- lm(y1 ~ x)

# draw the fit line on the plot
abline(y0.fit)
abline(y1.fit, col = "blue", lty=2)
#abline(myline3.fit, col = "blue")

legend(0.5, 0.5, legend=c("Fully connected topology", "90% connected random topology"),
       col=c("black", "blue"), lty=1:2, pch=c(0,15), cex=0.8)


png('time-q90f15r3.png', width=800, height=600, pointsize=18)
plot(x,t0, xlab="number of nodes", ylab="seconds", main="Python simulation with 90% quorum, 15% failure rate, 3 retries", ylim=c(0,1), xlim=c(0, 55), pch=0)
points(x,t1, pch=15, col="blue")
#points(x,y3, col="blue", pch=0)

# fit a line to the points
t0.fit <- lm(t0 ~ x)
t1.fit <- lm(t1 ~ x)

# draw the fit line on the plot
abline(t0.fit)
abline(t1.fit, col = "blue", lty=2)
#abline(myline3.fit, col = "blue")

legend(0.5, 0.5, legend=c("Fully connected topology", "90% connected random topology"),
       col=c("black", "blue"), lty=1:2, cex=0.8, pch=c(0,15))

png('sendrecv-q90f15r3.png', width=800, height=600, pointsize=18)
plot(x,s0, xlab="number of nodes", ylab="bytes", main="Python simulation with 90% quorum, 15% failure rate, 3 retries", ylim=c(0,13000), xlim=c(0, 55), pch=0)
points(x,s1, pch=15, col="blue")
points(x,r0, pch=2, col="red")
points(x,r1, pch=17, col="purple")

# fit a line to the points
s0.fit <- lm(s0 ~ x)
s1.fit <- lm(s1 ~ x)
r0.fit <- lm(r0 ~ x)
r1.fit <- lm(r1 ~ x)
#myline3.fit <-lm(y3 ~ x)
# get information about the fit
#summary(myline.fit)

# draw the fit line on the plot
abline(s0.fit)
abline(s1.fit, col = "blue", lty=2)
abline(r0.fit, col = "red", lty=3)
abline(r1.fit, col = "purple", lty=4)

legend(0, 11000, legend=c("Sent bytes, fully connected topology", "Sent bytes, 90% connected random topology", "Received bytes, fully connected topology", "Received bytes, 90% connected topology"),
       col=c("black", "blue", "red", "purple"), lty=1:4, cex=0.8, pch=c(0,2,15,17))
