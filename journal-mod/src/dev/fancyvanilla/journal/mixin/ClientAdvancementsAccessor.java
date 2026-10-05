package dev.fancyvanilla.journal.mixin;

import java.util.Map;
import net.minecraft.advancements.AdvancementHolder;
import net.minecraft.advancements.AdvancementProgress;
import net.minecraft.advancements.AdvancementTree;
import net.minecraft.client.multiplayer.ClientAdvancements;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.gen.Accessor;

/** Field names are identical in 26.2 and 26.3, unlike the getters and the listener interface. */
@Mixin(ClientAdvancements.class)
public interface ClientAdvancementsAccessor {
    @Accessor("tree")
    AdvancementTree fancyJournal$tree();

    @Accessor("progress")
    Map<AdvancementHolder, AdvancementProgress> fancyJournal$progress();
}
