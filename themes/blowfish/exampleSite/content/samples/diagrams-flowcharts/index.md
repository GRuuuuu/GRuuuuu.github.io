---
title: "Diagrams and Flowcharts"
date: 2019-03-06
description: "Guide to Mermaid usage in Blowfish"
summary: "It's easy to add diagrams and flowcharts to articles using Mermaid."
tags: ["mermaid", "sample", "diagram", "shortcodes"]
type: 'sample'
---

Mermaid diagrams are supported in Blowfish using the `mermaid` shortcode. Simply wrap the diagram markup within the shortcode. Blowfish automatically themes Mermaid diagrams to match the configured `colorScheme` parameter.

Refer to the [mermaid shortcode]({{< ref "docs/shortcodes#mermaid" >}}) docs for more details.

The examples below are a small selection taken from the [official Mermaid docs](https://mermaid-js.github.io/mermaid/). You can also [view the page source](https://raw.githubusercontent.com/nunocoracao/blowfish/main/exampleSite/content/samples/diagrams-flowcharts/index.md) on GitHub to see the markup.

## Flowchart

<div style="background-color:white; padding: 20px">
{{< mermaid >}}
graph TD
A[Christmas] -->|Get money| B(Go shopping)
B --> C{Let me think}
B --> G[/Another/]
C ==>|One| D[Laptop]
C -->|Two| E[iPhone]
C -->|Three| F[Car]
subgraph Section
C
D
E
F
G
end
{{< /mermaid >}}
</div>

## Sequence diagram

<div style="background-color:white; padding: 20px">
{{< mermaid >}}
sequenceDiagram
autonumber
par Action 1
Alice->>John: Hello John, how are you?
and Action 2
Alice->>Bob: Hello Bob, how are you?
end
Alice->>+John: Hello John, how are you?
Alice->>+John: John, can you hear me?
John-->>-Alice: Hi Alice, I can hear you!
Note right of John: John is perceptive
John-->>-Alice: I feel great!
loop Every minute
John-->Alice: Great!
end
{{< /mermaid >}}
</div>

## Class diagram

<div style="background-color:white; padding: 20px">
{{< mermaid >}}
classDiagram
Animal "1" <|-- Duck
Animal <|-- Fish
Animal <--o Zebra
Animal : +int age
Animal : +String gender
Animal: +isMammal()
Animal: +mate()
class Duck{
+String beakColor
+swim()
+quack()
}
class Fish{
-int sizeInFeet
-canEat()
}
class Zebra{
+bool is_wild
+run()
}
{{< /mermaid >}}
</div>

## Entity relationship diagram

<div style="background-color:white; padding: 20px">
{{< mermaid >}}
erDiagram
CUSTOMER }|..|{ DELIVERY-ADDRESS : has
CUSTOMER ||--o{ ORDER : places
CUSTOMER ||--o{ INVOICE : "liable for"
DELIVERY-ADDRESS ||--o{ ORDER : receives
INVOICE ||--|{ ORDER : covers
ORDER ||--|{ ORDER-ITEM : includes
PRODUCT-CATEGORY ||--|{ PRODUCT : contains
PRODUCT ||--o{ ORDER-ITEM : "ordered in"
{{< /mermaid >}}
</div>

