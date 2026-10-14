using UnityEngine;
using UnityEditor;
using TMPro;
using UnityEngine.TextCore.LowLevel;
using System.IO;
using System.Linq;
using System.Text;

public static class FontGen
{
    public static void Generate()
    {
        Debug.Log("[FontGen] start");
        if (!Directory.Exists("Assets/TextMesh Pro"))
        {
            Debug.Log("[FontGen] importing TMP Essentials...");
            TMP_PackageResourceImporter.ImportResources(true, false, false);
            AssetDatabase.Refresh();
            Debug.Log("[FontGen] essentials imported");
        }
        var font = AssetDatabase.LoadAssetAtPath<Font>("Assets/fusion.ttf");
        if (font == null) { Debug.LogError("[FontGen] fusion.ttf not loaded"); EditorApplication.Exit(2); return; }

        var chars = File.ReadAllText("Assets/charset.txt").Distinct().ToArray();
        Debug.Log("[FontGen] charset=" + chars.Length);

        var fontAsset = TMP_FontAsset.CreateFontAsset(
            font, 24, 5, GlyphRenderMode.SDFAA,
            2048, 2048, AtlasPopulationMode.Dynamic, false);
        if (fontAsset == null) { Debug.LogError("[FontGen] CreateFontAsset failed"); EditorApplication.Exit(3); return; }

        int ok = chars.Length;
        string missing;
        var faceLoaded = UnityEngine.TextCore.LowLevel.FontEngine.LoadFontFace(font, 24);
        Debug.Log($"[FontGen] LoadFontFace(font,24)={faceLoaded}");
        bool success = fontAsset.TryAddCharacters(new string(chars), out missing);
        if (!success || !string.IsNullOrEmpty(missing))
        {
            File.WriteAllText("Assets/missing.txt", missing ?? "");
            ok = chars.Length - (missing ?? "").Length;
        }
        Debug.Log($"[FontGen] added={ok} missing={(missing ?? "").Length}");
        if (ok > 0)
        {
            fontAsset.atlasPopulationMode = AtlasPopulationMode.Static;
            Debug.Log("[FontGen] population mode -> Static");
        }

        string assetPath = "Assets/CN_Font.asset";
        AssetDatabase.CreateAsset(fontAsset, assetPath);
        if (fontAsset.atlasTexture != null)
            AssetDatabase.AddObjectToAsset(fontAsset.atlasTexture, fontAsset);
        if (fontAsset.material != null)
            AssetDatabase.AddObjectToAsset(fontAsset.material, fontAsset);
        AssetDatabase.SaveAssets();

        var bundleName = "cnfont.bundle";
        var builds = new AssetBundleBuild[1];
        builds[0].assetBundleName = bundleName;
        builds[0].assetNames = new[] { assetPath };
        Directory.CreateDirectory("Assets/Out");
        var manifest = BuildPipeline.BuildAssetBundles(
            "Assets/Out", builds,
            BuildAssetBundleOptions.ChunkBasedCompression | BuildAssetBundleOptions.ForceRebuildAssetBundle,
            BuildTarget.StandaloneWindows64);

        Debug.Log("[FontGen] bundle=" + (manifest != null));
        Debug.Log("[FontGen] done ok=" + ok + "/" + chars.Length);
        EditorApplication.Exit(0);
    }
}
