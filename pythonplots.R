
# topology + Q 96% + 3 retries 
# 
# success rate: 0.27
# average time: 0.06312749
# average sent: 588.92
# average recv: 3114.55
# success rate: 0.15
# average time: 0.06250719
# average sent: 611.59
# average recv: 3093.79
# success rate: 0.1
# average time: 0.06274212
# average sent: 626.07
# average recv: 3044.86
# success rate: 0.03
# average time: 0.05964519
# average sent: 624.53
# average recv: 2935.86
# success rate: 0.01
# average time: 0.05616242
# average sent: 604.52
# average recv: 2828.07
# success rate: 0.0
# average time: 0.05619903
# average sent: 629.93
# average recv: 2683.31

x = c(0.05, 0.10, 0.15, 0.20, 0.25, 0.30) # message failure rate
y0 = c(1.0, 0.99, 0.77, 0.33, 0.01, 0.0) # connected topology success rate
y1 = c(0.27, 0.15, 0.1, 0.03, 0.01, 0.0 ) # random topology success rate

png('q96r3.png', width=800, height=600, pointsize=18)
plot(x,y0, xlab="message failure prob.", ylab="% success", main="Python simulations with 25 nodes, 96% quorum, 3 retries", ylim=c(0,1), xlim=c(0,0.35), pch=0)
points(x,y1, pch=0, col="blue")
#points(x,y3, col="blue", pch=0)

# fit a line to the points
myline.fit <- lm(y0 ~ x)
myline2.fit <-lm(y1 ~ x)
#myline3.fit <-lm(y3 ~ x)
# get information about the fit
#summary(myline.fit)

# draw the fit line on the plot
abline(myline.fit)
abline(myline2.fit, col = "blue", lty=2)
#abline(myline3.fit, col = "blue")

legend(0.2, 0.8, legend=c("Fully connected topology", "90% connected random topology"),
       col=c("black", "blue"), lty=1:2, cex=0.8)
