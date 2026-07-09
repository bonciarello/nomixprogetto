"""Test suite per il generatore di nomi progetto."""

import pytest
from nome_generatore import (
    tokenizza,
    categorizza_parola,
    trasforma_in_singolare,
    estrai_forma_imperativa,
    capitalizza,
    genera_nomi,
)


class TestTokenizza:
    """Test del tokenizer italiano."""

    def test_frase_semplice(self):
        parole = tokenizza("app per gestire le spese domestiche")
        assert "app" in parole
        assert "gestire" in parole
        assert "spese" in parole
        assert "domestiche" in parole
        # Stopwords rimosse
        assert "per" not in parole
        assert "le" not in parole

    def test_stopwords_rimosse(self):
        parole = tokenizza("il lo la i gli le un uno una")
        assert parole == []

    def test_parole_minime(self):
        parole = tokenizza("a b c")
        # Parole di 1 carattere ignorate
        assert len(parole) == 0

    def test_accenti(self):
        parole = tokenizza("perché è così")
        assert "così" in parole
        # "perché" e "è" sono stopwords
        assert "perché" not in parole


class TestCategorizza:
    """Test della categorizzazione parole."""

    def test_verbo_are(self):
        cat = categorizza_parola("gestire")
        assert "verbo" in cat

    def test_verbo_ere(self):
        cat = categorizza_parola("condividere")
        assert "verbo" in cat

    def test_verbo_ire(self):
        cat = categorizza_parola("dormire")
        assert "verbo" in cat

    def test_nome_zione(self):
        cat = categorizza_parola("applicazione")
        assert "nome" in cat

    def test_nome_mento(self):
        cat = categorizza_parola("strumento")
        assert "nome" in cat

    def test_aggettivo_bile(self):
        cat = categorizza_parola("amabile")
        assert "aggettivo" in cat

    def test_aggettivo_oso(self):
        cat = categorizza_parola("favoloso")
        assert "aggettivo" in cat

    def test_default_nome(self):
        cat = categorizza_parola("casa")
        assert "nome" in cat


class TestSingolare:
    """Test della trasformazione plurale → singolare."""

    def test_che_ca(self):
        assert trasforma_in_singolare("domestiche") == "domestica"

    def test_se_sa(self):
        assert trasforma_in_singolare("spese") == "spesa"

    def test_ni_no(self):
        assert trasforma_in_singolare("coinquilini") == "coinquilino"

    def test_i_o(self):
        assert trasforma_in_singolare("libri") == "libro"


class TestImperativa:
    """Test dell'estrazione della forma imperativa."""

    def test_are(self):
        imp = estrai_forma_imperativa("parlare")
        assert imp == "parla"

    def test_ere(self):
        imp = estrai_forma_imperativa("condividere")
        assert imp == "condividi"

    def test_ire(self):
        imp = estrai_forma_imperativa("dormire")
        assert imp == "dormi"


class TestCapitalizza:
    """Test della capitalizzazione."""

    def test_base(self):
        assert capitalizza("casa") == "Casa"

    def test_vuota(self):
        assert capitalizza("") == ""

    def test_gia_maiuscola(self):
        assert capitalizza("Casa") == "Casa"


class TestGeneraNomi:
    """Test della generazione nomi (integrazione)."""

    def test_input_valido_genera_nomi(self):
        nomi = genera_nomi(
            "app per gestire le spese domestiche condivise tra coinquilini"
        )
        assert isinstance(nomi, list)
        assert len(nomi) >= 5, f"Attesi almeno 5 nomi, ottenuti {len(nomi)}"

    def test_nomi_lunghezza(self):
        nomi = genera_nomi(
            "app per gestire le spese domestiche condivise tra coinquilini"
        )
        for nome in nomi:
            assert 4 <= len(nome) <= 30, f"Nome '{nome}' fuori range (len={len(nome)})"

    def test_nomi_unicita(self):
        nomi = genera_nomi(
            "app per gestire le spese domestiche condivise tra coinquilini",
            count=10,
        )
        assert len(nomi) == len(set(nomi)), "Nomi duplicati nella stessa chiamata"

    def test_input_vuoto(self):
        with pytest.raises(ValueError, match="Inserisci una descrizione"):
            genera_nomi("")

    def test_input_solo_spazi(self):
        with pytest.raises(ValueError, match="Inserisci una descrizione"):
            genera_nomi("   ")

    def test_input_troppo_corto(self):
        with pytest.raises(ValueError, match="almeno 3 parole"):
            genera_nomi("app bella")

    def test_input_minimo(self):
        """Con esattamente 3 parole significative deve funzionare."""
        nomi = genera_nomi("app per gestire progetti")
        assert len(nomi) >= 3

    def test_no_duplicati_con_nomi_esistenti(self):
        esistenti = {"SpesaCasa", "DividiTutto"}
        nomi = genera_nomi(
            "app per gestire le spese domestiche condivise tra coinquilini",
            nomi_esistenti=esistenti,
            count=8,
        )
        for nome in nomi:
            assert nome not in esistenti, f"Nome '{nome}' già presente tra gli esistenti"

    def test_nomi_con_caratteri_validi(self):
        nomi = genera_nomi(
            "app per gestire le spese domestiche condivise tra coinquilini",
            count=20,
        )
        for nome in nomi:
            # Solo caratteri alfanumerici (CamelCase)
            assert nome.replace(" ", "").isalnum(), f"Caratteri non validi in '{nome}'"

    def test_input_lungo_troncato(self):
        """Input > 500 caratteri viene troncato senza errori."""
        lungo = "app " * 200
        nomi = genera_nomi(lungo)
        assert len(nomi) >= 3

    def test_reso_noto(self):
        """Test specifico: deve generare nomi come SpesaConquista o DividiCasa."""
        nomi = genera_nomi(
            "app per gestire le spese domestiche condivise tra coinquilini",
            count=15,
        )
        # Verifica che generi nomi ragionevoli con componenti dell'input
        ha_spesa = any("Spesa" in n or "spesa" in n.lower() for n in nomi)
        ha_casa = any("Casa" in n or "casa" in n.lower() for n in nomi)
        ha_dividi = any(
            "Dividi" in n or "Condividi" in n or "dividi" in n.lower() for n in nomi
        )
        # Almeno uno dei pattern attesi deve comparire
        assert ha_spesa or ha_casa or ha_dividi, (
            f"Nessuno dei pattern attesi trovato nei nomi: {nomi}"
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
