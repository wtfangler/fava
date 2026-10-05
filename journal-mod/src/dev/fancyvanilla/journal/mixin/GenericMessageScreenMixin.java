package dev.fancyvanilla.journal.mixin;

import dev.fancyvanilla.journal.FvLoader;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.GuiGraphicsExtractor;
import net.minecraft.client.gui.screens.GenericMessageScreen;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/** Same backdrop for the plain message screens, i.e. "Saving world..." when you leave a world. The text is drawn after the background. */
@Mixin(GenericMessageScreen.class)
public abstract class GenericMessageScreenMixin {
    @Inject(method = "extractBackground", at = @At("TAIL"))
    private void fancyJournal$brand(GuiGraphicsExtractor g, int mouseX, int mouseY, float partial, CallbackInfo ci) {
        FvLoader.draw(Minecraft.getInstance(), g, g.guiWidth(), g.guiHeight(), 1f, -1f);
    }
}
