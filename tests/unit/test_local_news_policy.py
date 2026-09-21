from app.local_news_policy import has_local_context, is_local_source, local_story_decision


def test_only_registry_sources_are_accepted_as_local():
    assert is_local_source("https://www.midiamax.com.br/politica/teste")
    assert not is_local_source("https://www.bbc.com/portuguese/articles/teste")


def test_local_story_requires_source_and_territorial_evidence():
    assert local_story_decision(
        source_url="https://www.midiamax.com.br/politica/teste",
        title="Assembleia debate orçamento em Campo Grande",
    ) == "accept"
    assert local_story_decision(
        source_url="https://www.midiamax.com.br/esportes/teste",
        title="Vasco enfrenta Coritiba pelo Brasileirão",
    ) == "review"
    assert local_story_decision(
        source_url="https://www.bbc.com/portuguese/articles/teste",
        title="Governo anuncia medida internacional",
    ) == "reject"


def test_local_context_matches_state_and_cities():
    assert has_local_context("Safra em Mato Grosso do Sul", "")
    assert has_local_context("", "Obra atende Dourados")
    assert not has_local_context("Notícia nacional", "Sem relação regional")
