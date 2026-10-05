package dev.fancyvanilla.journal;

import net.minecraft.advancements.AdvancementType;
import net.minecraft.advancements.DisplayInfo;
import net.minecraft.network.chat.Component;
import net.minecraft.world.item.ItemStack;

/** Minecraft 26.3: DisplayInfo became a record. */
final class Compat {
    private Compat() { }

    static Component title(DisplayInfo d) { return d.title(); }

    static Component description(DisplayInfo d) { return d.description(); }

    static ItemStack icon(DisplayInfo d) { return d.icon().create(); }

    static AdvancementType type(DisplayInfo d) { return d.type(); }

    static boolean hidden(DisplayInfo d) { return d.hidden(); }
}
