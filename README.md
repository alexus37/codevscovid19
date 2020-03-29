# codevscovid19

## Init

Install tornado

```bash
    pip install tornado
```

## Start server

To start the server run:

```bash
    pip install -r requirements.txt
    python main.py
```

## Sample requests

Get the heatmap as json

```bash
    curl -X POST localhost:8888/heatmap
```

# Project Description

## Inspiration
In recent months, the Covid19 pandemic has shown to lead to death rates of up to 5% in cases of health care overloads. Switzerland is at the moment in a shutdown, trying to circumvent such a situation. There is much uncertainty on how to proceed after the quarantine, we are facing at the moment, since opening of stores and workplaces would lead to another major outbreak. We need effective solutions to enable us to live our daily lives, while still being able to keep the infection curve flat.
## What it does
By collecting movement profiles of Corona infected people, we are able to compute risk maps for users to avoid areas, which are associated with Corona infections. Furthermore, users can upload their movement profile in order to check their risk of having been contaminated. We compute this risk factor by integrating the risk values of the risk map over the trajectory of the uploaded user data.

The GDPR policy by the EU forced companies to provide an option to users for downloading their user data. We can exploit this for the Google Location History feature, where users can easily retrieve their movement profiles. By uploading their data, infected persons can contribute to up to date risk maps and healthy persons can use our website to evaluate their risk of having been infected based on their movement profile of the last couple of days.
## How we built it
Based on a collection of Google Location History data sets, we compute a 3D spatiotemporal infection risk map that reflects the risk of being infected when residing at or passing through places on that map. The map can be integrated over a trajectory to yield a risk score. This can be used to recommend users to stay at home or even get tested for SARS-CoV-2.

For the demo, we used GPS tracks in the Zurich area from the OpenStreetMap project. These GPS tracks represent movement profiles of positively tested people and form the basis for the risk map.
## Challenges we ran into

While, the user data retrieved by the Google Location history

## Accomplishments that we're proud of

We were a team of 4 developers and 2 communicators and managed to combine all our strengths into the project. Each single person was able to contribute a major part to the project, which enabled us to finish and even exceed our aims ahead of the time we planned. We are really proud of these team effort.

## What I learned

We focused on getting the project done in a professional fashion. We did not focus on learning about new technologies and tech stacks (which in itself is a cool aspect of Hackathons). We anyways learned a lot about team/project coordination and also feel a lot more comfortable with geolocation data, geological distance measures and maps visualizations.

## What's next for "Should I be worried"?

Publicity! If tested positively for SARS-CoV-2, people are able to contribute by (of course voluntarily) sharing their location history of the last one or two weeks. When done by enough people, this generates an invaluable resource for risk infections. Healthy persons can decide which regions to avoid and, based on their uploaded movement profile, get an idea of their risk of being infected in recent days.
