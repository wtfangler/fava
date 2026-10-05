package dev.fancyvanilla.journal.mixin;

import dev.fancyvanilla.journal.Journal;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.screens.Screen;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.ModifyVariable;

/** Swaps the vanilla advancements screen for the Fancy Vanilla journal, however it was opened (key or pause menu). */
@Mixin(Minecraft.class)
public abstract class MinecraftMixin {
    @ModifyVariable(method = "setScreenAndShow", at = @At("HEAD"), argsOnly = true)
    private Screen fancyJournal$replaceScreen(Screen screen) {
        return Journal.replace((Minecraft) (Object) this, screen);
    }
}
