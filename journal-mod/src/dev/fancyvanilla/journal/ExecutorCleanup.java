package dev.fancyvanilla.journal;

import java.util.concurrent.ExecutorService;
import java.util.concurrent.TimeUnit;

/** Drain texture work before Minecraft closes native images, without changing running animations. */
final class ExecutorCleanup {
    private ExecutorCleanup() { }

    static boolean stop(ExecutorService executor, long timeoutMillis) {
        executor.shutdown();
        try {
            if (executor.awaitTermination(timeoutMillis, TimeUnit.MILLISECONDS)) return true;
            executor.shutdownNow();
            return executor.awaitTermination(timeoutMillis, TimeUnit.MILLISECONDS);
        } catch (InterruptedException interrupted) {
            executor.shutdownNow();
            Thread.currentThread().interrupt();
            return executor.isTerminated();
        }
    }
}
