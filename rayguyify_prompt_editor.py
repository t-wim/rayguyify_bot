import streamlit as st
import json
from pathlib import Path

st.set_page_config(page_title="RayGuyify Prompt Editor", layout="wide")
st.title("🧠 RayGuyify Topic + AI Prompt Manager")

# Load topics and prompts
topics_file = Path("topics.json")
prompts_file = Path("rayguyify_ai_prompts.json")

if not topics_file.exists() or not prompts_file.exists():
    st.error("topics.json or rayguyify_ai_prompts.json not found.")
    st.stop()

topics = json.load(open(topics_file))
prompts = json.load(open(prompts_file))

# Sidebar navigation
topic_list = list(topics.keys())
selected = st.sidebar.selectbox("Select Topic", topic_list)
data = topics[selected]

st.subheader(f"🎯 Topic: {selected.upper()}")

# Editable fields
data["keywords"] = st.text_input("🔑 Keywords (comma-separated)", ", ".join(data.get("keywords", []))).split(",")
data["description"] = st.text_area("🧠 Description", value=data.get("description", ""))
data["default_scene"] = st.text_area("🎬 Default Scene", value=data.get("default_scene", ""))
data["default_caption"] = st.text_input("💬 Default Caption", value=data.get("default_caption", ""))

# Prompt preview and edit
def generate_prompt(scene, description):
    return (
        "Illustration of Ray Guy, a cartoon frog-like character wearing a hoodie and cap with the Raydium logo. "
        f"Scene: {scene} Mood: {description}. "
        "Style: crypto meme, bold lighting, dramatic composition, centered character, no text."
    )

prompt_default = generate_prompt(data["default_scene"], data["description"])
prompts[selected] = st.text_area("🧪 AI Prompt (auto-generated or custom)", value=prompts.get(selected, prompt_default), height=150)

# Save changes
if st.button("💾 Save Changes"):
    data["keywords"] = [k.strip() for k in data["keywords"] if k.strip()]
    topics[selected] = data
    with open(topics_file, "w", encoding="utf-8") as f:
        json.dump(topics, f, indent=2)
    with open(prompts_file, "w", encoding="utf-8") as f:
        json.dump(prompts, f, indent=2)
    st.success("✅ Changes saved!")

# Preview
with st.expander("🔍 Prompt Preview"):
    st.markdown(f"**Generated Prompt:**\n\n`{prompt_default}`")

with st.expander("📄 Raw JSON Output"):
    st.json({"topics.json": topics[selected], "rayguyify_ai_prompts.json": prompts[selected]})
