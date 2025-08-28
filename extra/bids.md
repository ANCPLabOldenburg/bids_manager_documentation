# What is BIDS? <img src="../static/bids/logo.jpg" alt="bids-logo" width="200px">
*"Neuroimaging experiments result in complex data that can be arranged in many different ways, and for a long time, there was no consensus on how to organize and share data obtained in neuroimaging experiments. **Brain Imaging Data Structure (BIDS)**, describes a simple and easy to adopt way of organizing neuroimaging and behavioral data"* (Gorgolewski et al., 2016; Niso et al., 2018). 

<img src="../static/bids/bids-order.jpg" alt="bids-order" width="600px" align="center">



The **[BIDS Specification](https://bids-specification.readthedocs.io/en/stable/)** defines the rules for data organizing and naming conventions. It is continuously updated thanks to community efforts. To ensure that the Specifications are implemented consistently, BIDS provides **[BIDS Schema](https://bids-specification.readthedocs.io/en/stable/appendices/schema.html)**, a machine readable representation written in YAML format. The BIDS Schema describes the different possible objects (BIDS concepts), rules (for naming filepaths and contents) and meta (the context to which rules can be applied).

<img src="../static/bids/bids-schema.png" alt="bids-schema" width="200px" align="center">

```{admonition} ancpBIDS

BIDS-Manager uses the [**ancpBIDS**](https://github.com/ANCPLabOldenburg/ancp-bids) library to handle BIDS datasets efficiently. This CLI library makes use of the BIDS specification and schema to load datasets, manage metada and write derivatives directly to your local drive; all in a structured and BIDS-compliant way.

Check out the [**ancpBIDS documentation**](https://ancplaboldenburg.github.io/ancpbids_documentation/index.html) for a full tutorial with examples.

```

```{admonition} Want to check more extra content?
:class: tip

Head back to the [main extra content page](../book/extra.md) to explore the others!

``` 
