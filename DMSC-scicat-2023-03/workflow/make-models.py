"""Create auxiliary models in SciCat."""
from pyscicat import model
from pyscicat.client import ScicatClient


def make_instrument(client: ScicatClient) -> None:
    instrument = model.Instrument(name="PeakMeister", customMetadata={"Real": False})
    print("instrument:", client.instruments_create(instrument))


def make_proposal(client: ScicatClient) -> None:
    proposal = model.Proposal(
        proposalId="276577",
        pi_email="Max.Novelli@ess.eu",
        pi_firstname="Massimiliano",
        pi_lastname="Novelli",
        email="Max.Novelli@ess.eu",
        firstname="Massimiliano",
        lastname="Novelli",
        title="DMSC SciCat Workshop 2023",
        abstract="Workshop on SciCat for DMSC in spring 2023",
        startTime="2023-03-22T00:00:00Z",
        ownerGroup="ess",
        accessGroups=["dmsc"],
    )
    print("proposal:", client.proposals_create(proposal))


def make_sample(client: ScicatClient) -> None:
    sample = model.Sample(
        owner="Massimiliano Novelli",
        description="Dummy sample for the SciCat Workshop at DMSC in spring 2023",
        ownerGroup="ess",
        accessGroups=["dmsc"],
    )
    print("sample:", client.samples_create(sample))


def main() -> None:
    client = ScicatClient("https://staging.scicat.ess.eu/api/v3", token="")
    make_instrument(client)
    make_proposal(client)
    make_sample(client)


if __name__ == "__main__":
    main()
