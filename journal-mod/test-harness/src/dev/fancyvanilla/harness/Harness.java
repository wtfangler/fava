package dev.fancyvanilla.harness;
import java.lang.reflect.Field;
import java.util.concurrent.CompletableFuture;
import net.minecraft.client.Minecraft;
import net.minecraft.client.Screenshot;
import net.minecraft.client.gui.screens.advancements.AdvancementsScreen;
import net.minecraft.server.MinecraftServer;
import net.minecraft.resources.Identifier;
import net.minecraft.resources.ResourceKey;
import net.minecraft.core.registries.Registries;
import net.minecraft.world.scores.ScoreHolder;

/** Test-only driver: complete-pack startup, progression regressions and journal layouts. */
public final class Harness {
    private static int stage, waited, total;
    private static CompletableFuture<Void> serverWork;
    private static int serverReadyAt=-1;
    private static void log(String text) { System.out.println("[FJ-HARNESS] " + text); }
    private static void check(boolean ok, String what) {
        if (!ok) throw new AssertionError(what);
        log("PASS " + what);
    }
    private static void command(MinecraftServer s, String text) {
        s.getCommands().performPrefixedCommand(s.createCommandSourceStack(), text);
    }
    private static Integer score(MinecraftServer s, String who, String objective) {
        var obj=s.getScoreboard().getObjective(objective);
        if(obj==null) return null;
        var value=s.getScoreboard().getPlayerScoreInfo(ScoreHolder.forNameOnly(who),obj);
        return value==null ? null : value.value();
    }
    private static boolean recipe(MinecraftServer s,String id) {
        return s.getPlayerList().getPlayers().getFirst().getRecipeBook().contains(
            ResourceKey.create(Registries.RECIPE,Identifier.parse("minecraft:"+id)));
    }
    private static boolean advancement(MinecraftServer s,String id) {
        var holder=s.getAdvancements().get(Identifier.parse(id));
        return holder!=null&&s.getPlayerList().getPlayers().getFirst().getAdvancements().getOrStartProgress(holder).isDone();
    }
    private static void work(Minecraft mc, Runnable task) {
        serverReadyAt=-1;
        serverWork=new CompletableFuture<>();
        mc.getSingleplayerServer().execute(() -> {
            try {task.run();serverWork.complete(null);}
            catch(Throwable t) {serverWork.completeExceptionally(t);}
        });
    }
    private static boolean complete() {
        if(!serverWork.isDone())return false;
        serverWork.join();
        // A server task finishing does not mean its packets reached the client.
        if(serverReadyAt<0)serverReadyAt=total;
        return total-serverReadyAt>=20;
    }
    private static boolean clientDone(Minecraft mc, String id) throws Exception {
        var accessor=Class.forName("dev.fancyvanilla.journal.mixin.ClientAdvancementsAccessor");
        var getter=accessor.getMethod("fancyJournal$progress");
        var progress=(java.util.Map<?,?>)getter.invoke(mc.getConnection().getAdvancements());
        for(var entry:progress.entrySet()) {
            if(((net.minecraft.advancements.AdvancementHolder)entry.getKey()).id().toString().equals(id)) {
                return ((net.minecraft.advancements.AdvancementProgress)entry.getValue()).isDone();
            }
        }
        return false;
    }
    private static void remember(String root, String filter) throws Exception {
        var type=Class.forName("dev.fancyvanilla.journal.JournalScreen");
        var field=type.getDeclaredField("rememberedRoot");field.setAccessible(true);field.set(null,root);
        var f=type.getDeclaredField("rememberedFilter");f.setAccessible(true);
        @SuppressWarnings({"unchecked","rawtypes"})
        var value=Enum.valueOf((Class)Class.forName("dev.fancyvanilla.journal.JournalScreen$Filter"),filter);
        f.set(null,value);
    }
    private static void open(Minecraft mc) {
        mc.gui.toastManager().clear();
        mc.setScreenAndShow(new AdvancementsScreen(mc.getConnection().getAdvancements()));
        check(mc.gui.screen().getClass().getName().equals("dev.fancyvanilla.journal.JournalScreen"),"journal replaces advancements");
        check(mc.gui.screen().isPauseScreen(),"journal preserves singleplayer pause");
    }
    private static void shot(Minecraft mc,String name) {
        mc.gui.toastManager().clear();
        Screenshot.grab(mc.gameDirectory,name+".png",mc.gameRenderer.mainRenderTarget(),1,c->log("saved "+name));
    }
    private static void next(){stage++;waited=0;}
    private static Object field(Object value,String name) throws Exception {
        var f=value.getClass().getDeclaredField(name);f.setAccessible(true);return f.get(value);
    }
    private static void checkLayout(Minecraft mc) throws Exception {
        var screen=mc.gui.screen();
        int px=(int)field(screen,"px"),pw=(int)field(screen,"pw");
        int chipX=(int)field(screen,"chipX"),chipW=(int)field(screen,"chipW");
        check(chipX+chipW*3+12<=px+pw,"all filter controls fit viewport");
        int top=(int)field(screen,"sbY"),bottom=top+(int)field(screen,"sbH");
        for(Object value:(java.util.List<?>)field(screen,"tabControls")) {
            var widget=(net.minecraft.client.gui.components.AbstractWidget)value;
            if(widget.visible) check(widget.getY()>=top&&widget.getY()+widget.getHeight()<=bottom,"visible tab hitbox stays inside sidebar");
        }
    }
    private static boolean containsEntry(Minecraft mc,String id) throws Exception {
        for(Object tab:(java.util.List<?>)field(mc.gui.screen(),"tabs")) {
            var entries=tab.getClass().getDeclaredMethod("entries");entries.setAccessible(true);
            for(Object entry:(java.util.List<?>)entries.invoke(tab)) {
                var holder=entry.getClass().getDeclaredMethod("holder");holder.setAccessible(true);
                if(((net.minecraft.advancements.AdvancementHolder)holder.invoke(entry)).id().toString().equals(id))return true;
            }
        }
        return false;
    }
    private static int tabCount(Minecraft mc,String id,String name) throws Exception {
        for(Object tab:(java.util.List<?>)field(mc.gui.screen(),"tabs")) {
            var root=tab.getClass().getDeclaredMethod("root");root.setAccessible(true);
            if(((net.minecraft.advancements.AdvancementNode)root.invoke(tab)).holder().id().toString().equals(id)) {
                var count=tab.getClass().getDeclaredMethod(name);count.setAccessible(true);
                return (int)count.invoke(tab);
            }
        }
        throw new AssertionError("Missing tab "+id);
    }
    public static void tick(Minecraft mc) {
        if ("loader".equals(System.getProperty("fj.scenario"))) {
            loaderTick(mc);
            return;
        }
        if ("epilog".equals(System.getProperty("fj.scenario"))) {
            epilogTick(mc);
            return;
        }
        journalTick(mc);
    }

    private static int loaderShots;

    /** Loader scenario: screenshots of the start-up overlay, then of the "saving world" message screen. */
    private static void loaderTick(Minecraft mc) {
        if (++total > 6000) { log("ERROR timeout"); mc.stop(); return; }
        try {
            if (mc.gui.overlay() != null) {
                if (total % 6 == 0 && loaderShots < 4) { shot(mc, "fj_l" + (++loaderShots) + "_loading"); }
                return;
            }
            if (mc.level == null || mc.player == null) return;
            waited++;
            if (waited == 60) {
                mc.setScreenAndShow(new net.minecraft.client.gui.screens.GenericMessageScreen(net.minecraft.network.chat.Component.translatable("menu.savingLevel")));
            } else if (waited == 75 || waited == 76) {
                if (waited == 75) shot(mc, "fj_l5_saving");
            } else if (waited > 110) {
                log("finished (loader shots=" + loaderShots + ")");
                mc.stop();
                stage = 99;
            }
        } catch (Throwable t) { log("ERROR " + t); t.printStackTrace(System.out); mc.stop(); stage = 99; }
    }

    private static final String EPILOG_ROOT = "tempered:bonus/epilog/root";

    /** Epilog scenario: gating before the dragon, unlock via vanilla kill_dragon, real inventory-triggered quests, screenshots. */
    private static void epilogTick(Minecraft mc) {
        if (++total > 9000) {
            log("ERROR timeout");
            mc.stop();
            return;
        }
        if (mc.level == null || mc.player == null || mc.getSingleplayerServer() == null) {
            return;
        }
        waited++;
        try {
            switch (stage) {
                case 0 -> {
                    if (waited > 100) {
                        work(mc, () -> {
                            var s = mc.getSingleplayerServer();
                            command(s, "advancement grant @a only tempered:age/1");
                            command(s, "advancement grant @a only tempered:age/3");
                            command(s, "give @a minecraft:firework_rocket 64");
                        });
                        next();
                    }
                }
                case 1 -> {
                    if (complete()) {
                        work(mc, () -> {
                            var s = mc.getSingleplayerServer();
                            check(!advancement(s, EPILOG_ROOT), "epilog root is locked before the dragon");
                            check(!advancement(s, "tempered:bonus/epilog/rocket_stock"), "epilog quest cannot count before the dragon");
                            check(advancement(s, "tempered:bonus/3/iron_guardian") == false, "era quest not done yet");
                            command(s, "advancement grant @a only minecraft:end/kill_dragon");
                        });
                        next();
                    }
                }
                case 2 -> {
                    if (complete() && waited > 40) {
                        work(mc, () -> {
                            var s = mc.getSingleplayerServer();
                            check(advancement(s, EPILOG_ROOT), "epilog root unlocks from the vanilla dragon advancement");
                            command(s, "give @a minecraft:firework_rocket 64"); // a vanilla single-item check looks at the changed stack
                            command(s, "give @a minecraft:elytra");
                            command(s, "give @a minecraft:dragon_egg");
                            command(s, "give @a minecraft:compass");
                            command(s, "give @a minecraft:clock");
                            command(s, "give @a minecraft:recovery_compass");
                            command(s, "give @a minecraft:ender_pearl 16");
                        });
                        next();
                    }
                }
                case 3 -> {
                    if (complete()) {
                        work(mc, () -> {
                            var s = mc.getSingleplayerServer();
                            check(advancement(s, "tempered:bonus/epilog/wings"), "epilog: elytra quest completes");
                            check(advancement(s, "tempered:bonus/epilog/dragon_egg"), "epilog: dragon egg quest completes");
                            check(advancement(s, "tempered:bonus/epilog/navigator_kit"), "epilog: navigator kit completes");
                            check(advancement(s, "tempered:bonus/epilog/rocket_stock"), "epilog: rocket stack counts once the root is unlocked");
                        });
                        next();
                    }
                }
                case 4 -> {
                    if (complete()) {
                        remember(EPILOG_ROOT, "ALL");
                        open(mc);
                        next();
                    }
                }
                case 5 -> { if (waited > 40) { checkLayout(mc); shot(mc, "fj_e1_epilog"); next(); } }
                case 6 -> {
                    if (waited > 20) {
                        mc.setScreenAndShow(null);
                        remember(EPILOG_ROOT, "DONE");
                        next();
                    }
                }
                case 7 -> { if (waited > 20) { open(mc); next(); } }
                case 8 -> { if (waited > 40) { shot(mc, "fj_e2_epilog_done"); next(); } }
                case 9 -> {
                    if (waited > 20) {
                        mc.setScreenAndShow(null);
                        remember("tempered:age/3", "ALL");
                        next();
                    }
                }
                case 10 -> { if (waited > 20) { open(mc); next(); } }
                case 11 -> { if (waited > 40) { checkLayout(mc); shot(mc, "fj_e3_era3"); next(); } }
                case 12 -> {
                    if (waited > 40) {
                        log("finished");
                        mc.stop();
                        stage = 99;
                    }
                }
                default -> { }
            }
        } catch (Throwable t) {
            log("ERROR " + t);
            t.printStackTrace(System.out);
            mc.stop();
            stage = 99;
        }
    }

    private static void journalTick(Minecraft mc) {
        if (++total > 7000) { log("ERROR timeout");mc.stop();return; }
        if (mc.level==null || mc.player==null) return;
        waited++;
        try {
            switch(stage) {
                case 0 -> {
                    if(waited>100) {
                        var s=mc.getSingleplayerServer();
                        work(mc,()->{
                            command(s,"gamemode creative @a");
                            command(s,"scoreboard players set OfflineProbe tempered.2m1 32");
                            command(s,"scoreboard players set OfflineProbe tempered.2m2 32");
                            command(s,"function tempered:admin/reset");
                            check(score(s,"OfflineProbe","tempered.2m1")==null && score(s,"OfflineProbe","tempered.2m2")==null,"reset clears offline copper counters");
                            command(s,"function tempered:admin/gate_on");
                            check(!recipe(s,"iron_pickaxe")&&!recipe(s,"copper_spear")&&!recipe(s,"netherite_spear_smithing"),"era1 locks native gear recipes");
                            command(s,"give @a minecraft:iron_ingot 12");
                            command(s,"give @a minecraft:oak_planks 12");
                            command(s,"give @a minecraft:stick 12");
                            command(s,"give @a minecraft:compass");
                            command(s,"give @a minecraft:filled_map");
                            check(!advancement(s,"tempered:bonus/3/survey_kit"),"future-era optional quest stays locked");
                        });next();
                    }
                }
                case 1 -> {
                    if(waited>40 && complete()) {
                        var s=mc.getSingleplayerServer();
                        work(mc,()->{
                            check(!recipe(s,"iron_pickaxe"),"inventory discovery cannot regrant locked recipe");
                            command(s,"function tempered:admin/gate_off");
                            check(recipe(s,"iron_pickaxe")&&score(s,"#gate","tempered.data")==0,"gate_off grants recipes");
                            command(s,"function tempered:core/init");
                            check(score(s,"#gate","tempered.data")==0&&recipe(s,"iron_pickaxe"),"gate_off persists init/reload path");
                            command(s,"function tempered:admin/gate_on");
                            check(!recipe(s,"iron_pickaxe"),"gate_on restores recipe gates");
                            command(s,"function tempered:admin/set_age {n:2}");
                            check(recipe(s,"copper_spear")&&!recipe(s,"iron_pickaxe"),"era2 unlocks copper but keeps iron locked");
                            command(s,"function tempered:admin/set_age {n:8}");
                            check(score(s,"#age","tempered.data")==2,"invalid era8 does not mutate progression");
                            command(s,"function tempered:admin/set_age {n:3}");
                            check(recipe(s,"iron_pickaxe"),"era3 unlocks iron recipe");
                            command(s,"clear @a minecraft:filled_map");
                            Integer before=score(s,"#done","tempered.data");
                            command(s,"give @a minecraft:filled_map");
                            check(advancement(s,"tempered:bonus/3/survey_kit"),"optional quest completes through natural inventory event");
                            check(java.util.Objects.equals(before,score(s,"#done","tempered.data")),"optional quest leaves shared era counter unchanged");
                            command(s,"scoreboard players reset #q.5b tempered.data");
                            command(s,"execute in minecraft:the_nether run tp @a 0 100 0");
                        });next();
                    }
                }
                case 2 -> {
                    if(waited>40 && complete()) {
                        var s=mc.getSingleplayerServer();
                        work(mc,()->{
                            command(s,"function tempered:check/5");
                            check(Integer.valueOf(1).equals(score(s,"#q.5b","tempered.data")),"Nether quest uses player dimension from overworld function");
                            command(s,"scoreboard players reset #q.6c tempered.data");
                            command(s,"execute in minecraft:the_end run tp @a 0 100 0");
                        });next();
                    }
                }
                case 3 -> {
                    if(waited>40 && complete()) {
                        var s=mc.getSingleplayerServer();
                        work(mc,()->{
                            command(s,"function tempered:check/6");
                            check(Integer.valueOf(1).equals(score(s,"#q.6c","tempered.data")),"End quest uses player dimension from overworld function");
                            command(s,"execute in minecraft:overworld run tp @a 0 100 0");
                            command(s,"function tempered:admin/set_age {n:7}");
                            check(advancement(s,"tempered:bonus/3/survey_kit"),"admin era change preserves optional quest progress");
                            for(int i=1;i<=7;i++)command(s,"advancement grant @a only tempered:age/"+i);
                            for(String id:new String[]{"1a","1b","1c","1d"})command(s,"advancement grant @a only tempered:quest/1/"+id);
                            for(String root:new String[]{"story","adventure","nether","end","husbandry"})command(s,"advancement grant @a only minecraft:"+root+"/root");
                            command(s,"advancement grant @a only fvtest:root");
                            command(s,"advancement grant @a only fvtest:visible_child");
                        });next();
                    }
                }
                case 4 -> {
                    if(waited>60&&complete()&&clientDone(mc,"tempered:age/7")&&clientDone(mc,"tempered:quest/1/1d")&&clientDone(mc,"fvtest:visible_child")&&clientDone(mc,"tempered:bonus/3/survey_kit")) { remember("tempered:age/1","ALL");open(mc);next(); }
                }
                case 5 -> {
                    if(waited>40) {
                        checkLayout(mc);check(!containsEntry(mc,"fvtest:hidden"),"known unfinished secret stays hidden");
                        check(tabCount(mc,"tempered:age/1","required")==9&&tabCount(mc,"tempered:age/1","requiredDone")==4,"original era1 progress remains four of nine");
                        check(tabCount(mc,"tempered:age/1","optional")==9,"nine optional goals are separate from era requirements");
                        check(tabCount(mc,"tempered:age/3","optionalDone")==1,"personal optional completion appears in journal");
                        shot(mc,"fj_1_wide");mc.setScreenAndShow(null);mc.options.guiScale().set(4);mc.resizeGui();remember("tempered:age/7","ALL");open(mc);next();
                    }
                }
                case 6 -> {
                    if(waited>40) {checkLayout(mc);shot(mc,"fj_2_compact_last_era");mc.setScreenAndShow(null);open(mc);next();}
                }
                case 7 -> {
                    if(waited>20) {
                        var f=mc.gui.screen().getClass().getDeclaredField("selectedId");f.setAccessible(true);
                        check("tempered:age/7".equals(f.get(mc.gui.screen())),"root selection persists after reopening");
                        mc.setScreenAndShow(null);
                        var s=mc.getSingleplayerServer();work(mc,()->command(s,"advancement grant @a only fvtest:hidden"));
                        next();
                    }
                }
                case 8 -> {
                    if(waited>40&&complete()&&clientDone(mc,"fvtest:hidden")) {remember("fvtest:root","ALL");open(mc);check(containsEntry(mc,"fvtest:hidden"),"completed secret becomes visible after server update");mc.setScreenAndShow(null);remember("tempered:age/1","DONE");open(mc);next();}
                }
                case 9 -> {
                    if(waited>40) {
                        shot(mc,"fj_3_done_filter");
                        mc.setScreenAndShow(null);
                        open(mc);
                        var method=Class.forName("dev.fancyvanilla.journal.Journal").getDeclaredMethod("openClassic",Minecraft.class,Class.forName("dev.fancyvanilla.journal.JournalScreen"));
                        method.setAccessible(true);method.invoke(null,mc,mc.gui.screen());
                        check(mc.gui.screen() instanceof AdvancementsScreen,"classic view remains accessible");next();
                    }
                }
                case 10 -> {if(waited>40){shot(mc,"fj_4_classic");mc.setScreenAndShow(new net.minecraft.client.gui.screens.PauseScreen(true));next();}}
                case 11 -> {
                    if(waited>40) {
                        net.minecraft.client.gui.components.Button button=null;
                        for(var child:mc.gui.screen().children()) {
                            if(child instanceof net.minecraft.client.gui.components.Button candidate&&candidate.getMessage().getString().contains("Dziennik"))button=candidate;
                        }
                        check(button!=null,"pause menu includes direct journal button");
                        boolean duplicate=false;net.minecraft.client.gui.components.Button statistics=null;
                        for(var child:mc.gui.screen().children()) {
                            if(child instanceof net.minecraft.client.gui.components.Button candidate) {
                                if(candidate.getMessage().equals(net.minecraft.network.chat.Component.translatable("gui.advancements")))duplicate=true;
                                if(candidate.getMessage().equals(net.minecraft.network.chat.Component.translatable("gui.stats")))statistics=candidate;
                            }
                        }
                        check(!duplicate,"pause menu no longer duplicates the vanilla advancements button");
                        check(statistics!=null&&statistics.getWidth()>button.getWidth(),"statistics button takes the freed pause-menu row");
                        check(button.getX()>=0&&button.getY()>=0&&button.getX()+button.getWidth()<=mc.gui.screen().width&&button.getY()+button.getHeight()<=mc.gui.screen().height,"pause journal button fits compact viewport");
                        shot(mc,"fj_5_pause_menu");button.onPress(null);next();
                    }
                }
                case 12 -> {
                    if(waited>20) {
                        check(mc.gui.screen().getClass().getName().equals("dev.fancyvanilla.journal.JournalScreen"),"pause button opens existing journal");
                        mc.gui.screen().onClose();
                        check(mc.gui.screen() instanceof net.minecraft.client.gui.screens.PauseScreen,"closing pause journal returns to pause menu");
                        mc.setScreenAndShow(null);
                        var mapping=(net.minecraft.client.KeyMapping)Class.forName("dev.fancyvanilla.journal.FancyJournalClient").getField("OPEN_JOURNAL").get(null);
                        net.minecraft.client.KeyMapping.click(mapping.getDefaultKey());
                        next();
                    }
                }
                case 13 -> {
                    if(waited>20) {
                        check(mc.gui.screen().getClass().getName().equals("dev.fancyvanilla.journal.JournalScreen"),"dedicated J key opens journal during gameplay");
                        mc.setScreenAndShow(null);
                        var s=mc.getSingleplayerServer();work(mc,()->{
                            Integer generation=score(s,"#bonus_generation","tempered.data");
                            command(s,"function tempered:admin/reset");
                            check(!advancement(s,"tempered:bonus/3/survey_kit"),"explicit reset clears personal optional progress");
                            check(score(s,"#bonus_generation","tempered.data")==generation+1,"explicit reset advances optional epoch");
                        });next();
                    }
                }
                case 14 -> {if(waited>20&&complete()){log("finished");mc.stop();stage=99;}}
                default -> {}
            }
        } catch(Throwable t) {log("ERROR "+t);t.printStackTrace(System.out);mc.stop();stage=99;}
    }
}
