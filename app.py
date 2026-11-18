import streamlit as st

from src import config
from src.ingest import count_chunks, ingest
from src.rag import ask, draft_ncr, root_cause

st.set_page_config(page_title="QMS Copilot", page_icon="🏭", layout="wide")
st.title("🏭 Quality Management Copilot")
st.caption("GenAI + RAG: apne SOP, NCR aur CAPA documents se sawaal poochho.")

# Pehli baar chalne par documents automatically index kar do
if "indexed" not in st.session_state:
    if count_chunks() == 0:
        with st.spinner("Documents index ho rahe hain (pehli baar thoda time lagega)..."):
            ingest()
    st.session_state.indexed = True

with st.sidebar:
    st.header("Documents")
    st.write(f"Indexed chunks: **{count_chunks()}**")
    uploaded = st.file_uploader("Naya document add karo", type=["txt", "md", "pdf"],
                                accept_multiple_files=True)
    if uploaded:
        for f in uploaded:
            (config.DATA_DIR / f.name).write_bytes(f.getvalue())
        st.success(f"{len(uploaded)} file save hui. Neeche Re-index dabao.")
    if st.button("Re-index documents"):
        with st.spinner("Indexing..."):
            n = ingest()
        st.success(f"{n} chunks index hue.")
        st.rerun()


def show_sources(hits):
    with st.expander("Sources (kin chunks se jawab bana)"):
        for h in hits:
            st.markdown(f"**{h['source']}**  (similarity {h['score']})")
            st.text(h["text"])


tab1, tab2, tab3 = st.tabs(["💬 Ask QMS", "📝 NCR / CAPA Draft", "🔍 Root Cause Analysis"])

with tab1:
    q = st.text_input("Sawaal likho", placeholder="Weld me porosity aaye to kya karna chahiye?")
    if st.button("Poochho", key="ask") and q:
        try:
            with st.spinner("Soch raha hoon..."):
                answer, hits = ask(q)
            st.markdown(answer)
            show_sources(hits)
        except Exception as e:
            st.error(str(e))

with tab2:
    desc = st.text_area(
        "Incident describe karo", height=150,
        placeholder="Line 3 par 12 brackets me crack mila, batch B-5120, final inspection me...",
    )
    if st.button("NCR + CAPA draft banao", key="ncr") and desc:
        try:
            with st.spinner("Draft ban raha hai..."):
                out, hits = draft_ncr(desc)
            st.markdown(out)
            st.download_button("Draft download (.txt)", out, file_name="ncr_capa_draft.txt")
            show_sources(hits)
        except Exception as e:
            st.error(str(e))

with tab3:
    problem = st.text_area("Problem statement", height=120, key="rca_problem",
                           placeholder="Batch B-4471 me porosity defect badh gaya.")
    method = st.radio("Method", ["5-Why", "Fishbone (Ishikawa)"], horizontal=True)
    if st.button("Analysis chalao", key="rca") and problem:
        try:
            with st.spinner("Analysis ho raha hai..."):
                out, hits = root_cause(problem, method)
            st.markdown(out)
            show_sources(hits)
        except Exception as e:
            st.error(str(e))
