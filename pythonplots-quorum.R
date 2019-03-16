x = c(1.0, 0.90, 0.80, 0.70, 0.60) # quorum levels
y0 = c(0.2, 1.0, 1.0, 1.0, 1.0)  # connected topology success rate
y1 = c(0.01, 0.48, 0.89, 0.99, 1.0) # random topology success rate

png('f15r3.png', width=800, height=600, pointsize=18)
plot(x,y0, xlab="quorum level", ylab="% success", main="Python simulations with 25 nodes, 15% failure rate, 3 retries", ylim=c(0,1), xlim=c(0.5, 1.0), pch=0)
points(x,y1, pch=0, col="blue")
#points(x,y3, col="blue", pch=0)

# fit a line to the points
myline.fit <- lm(y0 ~ x)
myline2.fit <-lm(y1 ~ x)
#myline3.fit <-lm(y3 ~ x)
# get information about the fit
#summary(myline.fit)

# draw the fit line on the plot
#abline(myline.fit)
abline(myline2.fit, col = "blue", lty=2)
#abline(myline3.fit, col = "blue")

legend(0.5, 0.5, legend=c("Fully connected topology", "90% connected random topology"),
       col=c("black", "blue"), lty=1:2, cex=0.8)
