package dev.fancyvanilla.journal;

import com.mojang.blaze3d.platform.InputConstants;
import java.lang.reflect.Field;
import java.lang.reflect.Modifier;
import java.util.List;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.ThreadPoolExecutor;
import net.fabricmc.api.ClientModInitializer;
import net.fabricmc.fabric.api.client.event.lifecycle.v1.ClientLifecycleEvents;
import net.fabricmc.fabric.api.client.event.lifecycle.v1.ClientTickEvents;
import net.fabricmc.fabric.api.client.keymapping.v1.KeyMappingHelper;
import net.fabricmc.fabric.api.client.screen.v1.ScreenEvents;
import net.fabricmc.fabric.api.client.screen.v1.Screens;
import net.fabricmc.loader.api.FabricLoader;
import net.minecraft.client.KeyMapping;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.components.AbstractWidget;
import net.minecraft.client.gui.components.Button;
import net.minecraft.client.gui.components.Tooltip;
import net.minecraft.client.gui.screens.PauseScreen;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.network.chat.Component;

/** Journal entry points and optional texture executor cleanup. */
public final class FancyJournalClient implements ClientModInitializer {
    public static KeyMapping OPEN_JOURNAL;
    private static final String ANIMATED_TEXTURE = "io.github.foundationgames.animatica.animation.AnimatedTexture";

    @Override
    public void onInitializeClient() {
        OPEN_JOURNAL = KeyMappingHelper.registerKeyMapping(new KeyMapping(
                "key.fancy_journal.open", InputConstants.KEY_J, KeyMapping.Category.GAMEPLAY));
        ClientTickEvents.END_CLIENT_TICK.register(client -> {
            while (OPEN_JOURNAL.consumeClick()) {
                if (client.level != null && client.getConnection() != null && client.gui.screen() == null) {
                    Journal.open(client, null);
                }
            }
        });
        ScreenEvents.AFTER_INIT.register(FancyJournalClient::addPauseEntry);
        if (!FabricLoader.getInstance().isModLoaded("animatica")) return;
        try {
            Class<?> texture = Class.forName(ANIMATED_TEXTURE, false, getClass().getClassLoader());
            try {
                // Animatica 0.6.3 already registers its own lifecycle cleanup. Leave that implementation in charge.
                texture.getDeclaredMethod("shutdownExecutor");
                Journal.LOGGER.info("Animatica provides its own executor cleanup");
                return;
            } catch (NoSuchMethodException legacyRelease) {
                // The verified 26.3 release 0.6.2 has only this public, static executor field.
            }
            Field field = texture.getField("EXECUTORS");
            if (!Modifier.isStatic(field.getModifiers()) || !ExecutorService.class.isAssignableFrom(field.getType())) {
                Journal.LOGGER.warn("Animatica executor shape differs; compatibility cleanup was not installed");
                return;
            }
            ClientLifecycleEvents.CLIENT_STOPPING.register(client -> closeAnimations(field));
            Journal.LOGGER.info("Registered legacy Animatica texture executor cleanup for client shutdown");
        } catch (ReflectiveOperationException | LinkageError failure) {
            Journal.LOGGER.warn("Could not inspect Animatica executor; compatibility cleanup was not installed", failure);
        }
    }

    private static void addPauseEntry(Minecraft client, Screen screen, int width, int height) {
        if (!(screen instanceof PauseScreen pause) || !pause.showsPauseMenu() || client.getConnection() == null) return;
        List<AbstractWidget> widgets = Screens.getWidgets(screen);
        for (AbstractWidget widget : widgets) {
            if (widget instanceof Button && widget.getMessage().equals(Component.translatable("menu.returnToGame"))) {
                // Share the existing full-width row: no extra height or interference with menu extensions.
                int gap = 8;
                int originalWidth = widget.getWidth();
                int buttonWidth = (originalWidth - gap) / 2;
                if (buttonWidth < 90) {
                    Journal.LOGGER.warn("Pause menu return button is too narrow for a journal entry");
                    return;
                }
                widget.setWidth(buttonWidth);
                Button entry = Button.builder(Component.translatable("fancy_journal.open_button", OPEN_JOURNAL.getTranslatedKeyMessage()),
                                ignored -> Journal.open(client, pause))
                        .bounds(widget.getX() + buttonWidth + gap, widget.getY(), originalWidth - buttonWidth - gap, widget.getHeight())
                        .tooltip(Tooltip.create(Component.translatable("fancy_journal.open_tooltip", OPEN_JOURNAL.getTranslatedKeyMessage())))
                        .build();
                widgets.add(entry);
                replaceVanillaAdvancementsButton(widgets);
                return;
            }
        }
    }

    /**
     * The journal is the only progress screen: drop the vanilla "Advancements" button (it would open the same journal)
     * and let "Statistics" use the whole row so the pause menu stays tidy.
     */
    private static void replaceVanillaAdvancementsButton(List<AbstractWidget> widgets) {
        Button advancements = null;
        Button statistics = null;
        for (AbstractWidget widget : widgets) {
            if (!(widget instanceof Button button)) continue;
            Component label = button.getMessage();
            if (label.equals(Component.translatable("gui.advancements"))) advancements = button;
            else if (label.equals(Component.translatable("gui.stats"))) statistics = button;
        }
        if (advancements == null) return;
        if (statistics != null && statistics.getY() == advancements.getY()) {
            int left = Math.min(statistics.getX(), advancements.getX());
            int right = Math.max(statistics.getX() + statistics.getWidth(), advancements.getX() + advancements.getWidth());
            statistics.setX(left);
            statistics.setWidth(right - left);
        }
        widgets.remove(advancements);
    }

    private static void closeAnimations(Field field) {
        try {
            ExecutorService executor = (ExecutorService) field.get(null);
            if (executor instanceof ThreadPoolExecutor pool) {
                // Do not start this thread: its factory name identifies the pool from a shutdown thread dump.
                Thread diagnostic = pool.getThreadFactory().newThread(() -> { });
                Journal.LOGGER.info("Stopping legacy Animatica executor: thread={}, daemon={}, workers={}, queued={}",
                        diagnostic.getName(), diagnostic.isDaemon(), pool.getPoolSize(), pool.getQueue().size());
            }
            boolean stopped = ExecutorCleanup.stop(executor, 2000);
            if (stopped) {
                Journal.LOGGER.info("Legacy Animatica executor terminated");
            } else {
                Journal.LOGGER.warn("Legacy Animatica executor did not terminate within the shutdown timeout");
            }
        } catch (ReflectiveOperationException | RuntimeException failure) {
            Journal.LOGGER.warn("Could not close legacy Animatica texture executor", failure);
        }
    }
}
