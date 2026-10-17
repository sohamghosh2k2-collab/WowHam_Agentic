# Deep-tech trajectory patterns

Common patterns seen in past deep-tech company paths. Use them to name the
pattern a startup is in and the risks that come with it. Each pattern is linked
to cases in `data/trajectories/reference_cases.jsonl` (field `patterns`).
Add new patterns as you learn them, and cite your evidence.

## P1. Science-to-product valley of death
Strong lab results, but the step from prototype to a manufacturable,
reliable product takes much longer and costs more than planned.
**Signals:** a founding team of only researchers, TRL ≤ 4 at Series A, no
hires with manufacturing or process engineering experience.
**Mitigants:** an early industrial partner, grant money for the non-dilutive
de-risking, a pilot line before the large fab.

## P2. Capital intensity outruns the funding market
Hardware or energy companies that need heavy capex before revenue. They're
exposed when funding conditions get tighter. Some fail even with real technology.
**Signals:** a plan that needs several $100M+ rounds before first revenue, one
plant or one product line, debt financing a factory.
**Mitigants:** offtake agreements, government loans or grants, a modular or
licensing model.

## P3. Verification gap / claims ahead of evidence
Public claims go further than what independent parties have verified.
**Signals:** no peer-reviewed or third-party validation, secrecy presented as
"IP protection", a board without domain experts, demos that nobody can repeat.
**Action:** treat this as a red flag. Score technical_risk ≤ 2 until there is
independent validation.

## P4. Platform-to-product pivot
A broad technology platform finds traction only once it focuses on one
application with a clear buyer. Narrowing down early tends to beat staying broad.
**Signals:** many "potential applications" and no named design partner.

## P5. Government-first commercialisation
Defense, space and energy companies that use government contracts (e.g.
SBIR, ARPA-E, EIC) as a bridge to commercial markets.
**Signals:** stacked grants and contracts, dual-use positioning.
**Risk:** dependence on budget cycles and slow procurement.

## P6. Infrastructure/timing tailwind
A company whose market opens up because a cost curve, regulation or a platform
shift arrives at the right time (e.g. falling launch costs for space, GPU
demand for AI chips, subsidies for clean energy).
**Check:** is the tailwind still accelerating, or already priced in?

## P7. Incumbent response
When the market is proven, incumbents with manufacturing scale move in.
Startups win by being much better on one dimension that matters, or through
a part of the market the incumbent can't serve.

## P8. Hype-cycle financing (SPAC/peak valuation)
Companies that go public or raise at peak-cycle valuations before reaching
their technical milestones often struggle afterwards (down rounds, dilution).
**Signals:** valuation based on projections 5+ years out, little revenue.

## P9. Talent-dense acquisition outcome
Research-heavy teams in hot fields often end up acquired for their team and
IP before reaching standalone scale. This is a decent outcome for early
investors, but it caps the upside.
