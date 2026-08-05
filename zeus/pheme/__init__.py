# zeus/pheme/ - Pheme: news consolidation and analysis subsystem.
#
# Pheme (personification of rumor and public report) ingests consolidated news
# from Canary and CapitolScope into the zeus_news collection, runs a staged
# local-only analytical pipeline (extract -> cluster -> thread -> correlate ->
# rank -> synthesize), and delivers a daily digest plus gated breaking alerts.
#
# All analytical LLM calls are pinned to local Ollama via pheme_llm_call();
# nothing in this package may route onto the cloud small-LLM chain.
