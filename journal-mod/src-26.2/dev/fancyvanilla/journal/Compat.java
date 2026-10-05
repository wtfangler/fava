package dev.fancyvanilla.journal;

import net.minecraft.advancements.AdvancementType;
import net.minecraft.advancements.DisplayInfo;
import net.minecraft.network.chat.Component;
import net.minecraft.world.item.ItemStack;

/** Minecraft 26.2: DisplayInfo is a class with getters. */
final class Compat {
    private Compat() { }

    static Component title(DisplayInfo d) { return d.getTitle(); }

    static Component description(DisplayInfo d) { return d.getDescription(); }

    static ItemStack icon(DisplayInfo d) { return d.getIcon().create(); }

    static AdvancementType type(DisplayInfo d) { return d.getType(); }

    static boolean hidden(DisplayInfo d) { return d.isHidden(); }
}
