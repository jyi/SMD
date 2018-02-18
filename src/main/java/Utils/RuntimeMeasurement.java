package Utils;

public class RuntimeMeasurement {
    private long startingTime, startingMemory;
    private long finishingTime, finishingMemory;

    private static long getMemoryUsed(){
        return Runtime.getRuntime().totalMemory()-Runtime.getRuntime().freeMemory();
    }

    public void logStartingTimeAndMemory(){
        startingTime = System.currentTimeMillis();
        startingMemory = getMemoryUsed();
    }

    public void logFinishingTimeAndMemory(){
        finishingTime = System.currentTimeMillis();
        finishingMemory = getMemoryUsed();
    }

    public double getTimeSpentInSeconds(){
        return (finishingTime - startingTime) / 1000.0;
    }

    public double getMemorySpentInMegabytes(){
        return (finishingMemory - startingMemory) / Math.pow(2, 20);
    }
}
