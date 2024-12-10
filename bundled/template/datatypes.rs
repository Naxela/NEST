use std::collections::HashMap;
use bevy::{asset::Handle, gltf::Gltf, prelude::{AnimationGraph, AnimationNodeIndex, Component, Resource}, scene::Scene};
use serde::Deserialize;


#[derive(Resource, Default)]
pub struct LoadingStages {
    pub gltf_load: bool,
    pub gltf_spawned: bool,
    pub lightmap_registry: bool,
    pub lightmap_textures: bool,
    pub audio: bool,
    pub camlights: bool,
}

#[derive(Resource, Debug)]
pub struct GLTFScene(pub Handle<Scene>);

#[derive(Deserialize, Debug)]
pub struct GltfExtrasValue {
    #[serde(rename = "TLM_Lightmap")]
    pub tlm_lightmap: Option<String>,
}

#[derive(Component)]
pub struct LightmapInfo {
    pub lightmap_name: String,
    pub exposure: f32,
}

#[derive(Resource, Debug, Default)]
pub struct LightmapRegistry {
    pub map: HashMap<String, String>,
}

#[derive(Resource)]
pub struct Animations {
    pub animations: Vec<AnimationNodeIndex>, // Store node indices for each animation
    pub graph: Handle<AnimationGraph>,
}

#[derive(Resource)]
pub struct GltfHandleResource(pub Handle<Gltf>); // Wrap Handle<Gltf> in a struct that implements Resource

#[derive(Debug, Clone, Deserialize)]
pub struct MaterialOptions {
    pub outline: Option<f32>,
    pub interact: Option<bool>,
}