package dev.fancyvanilla.journal;

import dev.fancyvanilla.journal.mixin.AdvancementsScreenAccessor;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.client.gui.screens.advancements.AdvancementsScreen;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public final class Journal {
    public static final Logger LOGGER = LoggerFactory.getLogger("fancy_journal");
    private static boolean bypass;

    private Journal() {
    }

    public static void open(Minecraft mc, Screen lastScreen) {
        if (mc.getConnection() != null) {
            mc.setScreenAndShow(new AdvancementsScreen(mc.getConnection().getAdvancements(), lastScreen));
        }
    }

    /** Called for every screen that is about to be shown. Hold Shift while opening to get the classic view. */
    public static Screen replace(Minecraft mc, Screen screen) {
        if (bypass || !(screen instanceof AdvancementsScreen classic) || mc.hasShiftDown()) {
            return screen;
        }
        try {
            AdvancementsScreenAccessor accessor = (AdvancementsScreenAccessor) classic;
            return new JournalScreen(accessor.fancyJournal$advancements(), accessor.fancyJournal$lastScreen());
        } catch (Throwable t) {
            LOGGER.error("Could not open the Fancy Vanilla journal, using the classic advancements screen", t);
            return screen;
        }
    }

    public static void openClassic(Minecraft mc, JournalScreen from) {
        bypass = true;
        try {
            mc.setScreenAndShow(new AdvancementsScreen(from.advancements(), from.lastScreen()));
        } finally {
            bypass = false;
        }
    }
}
