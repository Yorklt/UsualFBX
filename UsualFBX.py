import os
import bpy
from enum import Enum

# メッセージ関数の定義
def show_message(message = "", title = "Message", icon = "INFO"):
    def draw(self, context):
        self.layout.label(text = message)
    bpy.context.window_manager.popup_menu(draw, title = title, icon = icon)

# 出力タイプの定義
class ExportType(Enum):
    ONLY_OBJS = 0
    ONLY_ANIMS = 1
    OBJS_AND_ANIMS = 2

# コア関数の定義
def ExportFBX(filename: str, exp_type: ExportType, obj_names: list[str], scale: float):
    
    # フルパスの生成
    if bpy.data.filepath is None:
        show_message("エラー", "保存するフォルダが見つかりません。実行前に、まずはこのblendファイル自体をどこかに保存してください。" , "ERROR")
        return
    filepath = os.path.join(os.path.dirname(bpy.data.filepath), filename)

    # 一部のオブジェクトだけ出力
    if (obj_names is not None) and (len(obj_names) > 0):
        # すべてのオブジェクトを選択解除
        for object in bpy.data.objects:
            object.select_set(False)

        # オブジェクト選択
        for obj_name in obj_names:
            if obj_name in bpy.data.objects:
                # Select Object
                object = bpy.data.objects[obj_name]
                object.hide_viewport = False
                object.hide_set(False)
                object.hide_select = False
                object.select_set(True)
            else:
                show_message("エラー", "オブジェクト" + obj_name + "が見つかりません。" , "ERROR")
                return

    # 現在のフレームを0にする
    if (exp_type == ExportType.ONLY_ANIMS) or (exp_type == ExportType.OBJS_AND_ANIMS):
        bpy.context.scene.frame_current = 0

    # 選択オブジェクトだけ出力するかどうか
    use_selection: bool
    if (obj_names is not None) and (len(obj_names) > 0):
        use_selection = True
    else:
        use_selection = False
        
    # アニメーションを出力するかどうか
    bake_anim: bool
    if exp_type == ExportType.ONLY_OBJS:
        bake_anim = False
    if exp_type == ExportType.ONLY_ANIMS:
        bake_anim = True
    if exp_type == ExportType.OBJS_AND_ANIMS:
        bake_anim = True
        
    # アニメーションの簡略化設定
    # （0にするとスムーズになりますがファイルサイズが大きくなります）
    bake_anim_simplify_factor = 1.0
    
    # 標準エクスポーターの呼び出し
    bpy.ops.export_scene.fbx(
        filepath = filepath, # not default
        check_existing = True,
        filter_glob = ".fbx",
        use_selection = use_selection, # not default
        use_visible = False,
        use_active_collection = False,
        global_scale = scale, # not default
        apply_unit_scale = True,
        apply_scale_options = "FBX_SCALE_NONE",
        use_space_transform = True,
        bake_space_transform = False,
        object_types = {"ARMATURE", "EMPTY", "MESH"}, # not default
        use_mesh_modifiers = True,
        mesh_smooth_type = "OFF",
        use_subsurf = False,
        use_mesh_edges = False,
        use_tspace = False,
        use_triangles = False,
        use_custom_props = False,
        add_leaf_bones = True,
        primary_bone_axis = "Y",
        secondary_bone_axis = "X",
        use_armature_deform_only = False,
        armature_nodetype = "NULL",
        bake_anim = bake_anim, # not default
        bake_anim_use_all_bones = True,
        bake_anim_use_nla_strips = False, # not default
        bake_anim_use_all_actions = True,
        bake_anim_force_startend_keying = True,
        bake_anim_step = 1.0,
        bake_anim_simplify_factor = bake_anim_simplify_factor, # not default,
        path_mode = "AUTO",
        embed_textures = False,
        batch_mode = "OFF",
        use_batch_own_dir = True,
        use_metadata = True,
        axis_forward = "-Z",
        axis_up = "Y"
        )
        
    show_message("出力しました", filepath, "INFO")

# Usual FBX
# 使い方
# 1. BlenderのUIをテキストエディタに切り替えます。
# 2. テキストエディタの「＋新規」をクリックして新規テキストを作ります。
# 3. このテキストを貼り付けます。
# 4. サンプルを参考に、出力したい内容を書き加えます。
# 5. テキストエディタの再生ボタン、またはAlt+Pで実行！

# ExportFBXのパラメータについて
# 1番目: ファイル名。"Hero.fbx"みたいに、後ろにfbxを付けてください。
# 2番目: ONLY_OBJS→オブジェクトのみ ONLY_ANIMS→アニメのみ OBJS_AND_ANIMS→両方
# 3番目: 出力するオブジェクトを絞り込みます。すべて出力するときはNoneにしてください。
# 4番目: スケール。1.0とか0.01とか。

# 例
# ダミーパーツを除外してアニメーションと一緒に出力
# obj_names = []
# obj_names.append("Armature")
# obj_names.append("MyHero")
# ExportFBX("MyHero.fbx", ExportType.OBJS_AND_ANIMS, obj_names, 1.0)

# 例
# サブパーツを変えて複数出力する（アニメは別途出力）
# obj_names = []
# obj_names.append("Armature")
# obj_names.append("MainBody")
# obj_names.append("SubBody_A")
# ExportFBX("MyCharacter_A.fbx", ExportType.ONLY_OBJS, obj_names, 1.0)
# obj_names = []
# obj_names.append("Armature")
# obj_names.append("MainBody")
# obj_names.append("SubBody_B")
# ExportFBX("MyCharacter_B.fbx", ExportType.ONLY_OBJS, obj_names, 1.0)

# 例
# アニメーションのみ出力
# obj_names = []
# obj_names.append("Armature")
# ExportFBX("Fungus_Anim.fbx", ExportType.ONLY_ANIMS, obj_names, 1.0)

# 例
# 同じBlend内のオブジェクトを個別にすべて出力する（スケール0.01倍）
# ExportFBX("MyMapObjA.fbx", ExportType.ONLY_OBJS, ["ObjA"], 0.01)
# ExportFBX("MyMapObjB.fbx", ExportType.ONLY_OBJS, ["ObjB"], 0.01)
# ExportFBX("MyMapObjC.fbx", ExportType.ONLY_OBJS, ["ObjC"], 0.01)

# 例
# オブジェクトをすべて出力する（スケール10倍）
# ExportFBX("MyField.fbx", ExportType.ONLY_OBJS, None, 10)

# ----------------------------
# ここから下を書き換えてください。

obj_names = []
ExportFBX("sample.fbx", ExportType.ONLY_OBJS, obj_names, 1.0)

