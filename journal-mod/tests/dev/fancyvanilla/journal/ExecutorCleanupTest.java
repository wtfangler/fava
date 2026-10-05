package dev.fancyvanilla.journal;

import java.util.List;
import java.util.concurrent.CopyOnWriteArrayList;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;

/** Verify the real non-daemon executor can drain and stop, without changing thread factories or calling System.exit. */
public final class ExecutorCleanupTest {
    private static void check(boolean value, String message) {
        if (!value) throw new AssertionError(message);
    }

    public static void main(String[] args) throws Exception {
        List<Thread> threads = new CopyOnWriteArrayList<>();
        var factory = Executors.defaultThreadFactory();
        ExecutorService pool = Executors.newFixedThreadPool(4, task -> {
            Thread thread = factory.newThread(task);
            threads.add(thread);
            return thread;
        });
        AtomicInteger completed = new AtomicInteger();
        for (int i = 0; i < 64; i++) pool.submit(completed::incrementAndGet);
        check(ExecutorCleanup.stop(pool, 2000), "Drain completes within timeout");
        check(completed.get() == 64, "Queued frame work drained");
        for (Thread thread : threads) {
            check(!thread.isDaemon(), "Normal thread factory remains unchanged");
            thread.join(1000);
            check(!thread.isAlive(), "No worker keeps the JVM alive");
        }

        CountDownLatch started = new CountDownLatch(1), blocked = new CountDownLatch(1);
        AtomicInteger interrupted = new AtomicInteger();
        ExecutorService stalled = Executors.newSingleThreadExecutor();
        stalled.submit(() -> {
            started.countDown();
            try { blocked.await(); } catch (InterruptedException expected) { interrupted.incrementAndGet(); }
        });
        check(started.await(1, TimeUnit.SECONDS), "Stalled job started");
        check(ExecutorCleanup.stop(stalled, 100), "Timeout interrupts stalled work and terminates");
        check(interrupted.get() == 1, "Stalled job interrupted once");

        ExecutorService interruptPath = Executors.newFixedThreadPool(4);
        interruptPath.submit(() -> { });
        Thread.currentThread().interrupt();
        ExecutorCleanup.stop(interruptPath, 100);
        check(Thread.interrupted(), "Caller interrupt status preserved");
        check(interruptPath.awaitTermination(1, TimeUnit.SECONDS), "Interrupt path still shuts down workers");
        System.out.println("ExecutorCleanup: queued work drain, non-daemon worker termination, timeout and interrupt preservation passed");
    }
}
