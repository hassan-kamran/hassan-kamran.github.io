FedGAN: A Privacy-Preserving Framework for Synthetic Data Generation
Artificial intelligence
2025-03-23
fedgan.avif
Discover FedGAN, a novel privacy-preserving framework that enables medical institutions to collaboratively train AI models for diabetic retinopathy detection without sharing sensitive patient data. Learn how this federated learning approach with GANs maintains data privacy while generating high-quality synthetic images.

# FedGAN: A Privacy-Preserving Framework for Diabetic Retinopathy Classification Using Cross-Silo Federated Learning and Synthetic Data

## Introduction

Deep learning has revolutionized medical image analysis, achieving performance that rivals or even surpasses human capabilities in certain diagnostic tasks. In healthcare, this presents an unprecedented opportunity to integrate AI into clinical workflows, enhancing the accuracy, efficiency, and cost-effectiveness of diagnoses.

However, developing robust medical AI models faces two major obstacles: the need for large volumes of training data and the strict privacy regulations governing patient information. Healthcare institutions worldwide possess valuable medical data repositories, but sharing this sensitive data is severely restricted by regulations such as HIPAA, GDPR, and other region-specific privacy laws.

This blog post introduces **FedGAN** - a privacy-preserving federated learning framework for generating synthetic medical images that addresses these fundamental challenges.

## The Challenge: Privacy vs. Data Utility in Medical AI

Medical AI development presents a fundamental dilemma: models require extensive, diverse data for optimal performance, but patient privacy regulations restrict data sharing between institutions. Traditional approaches often force compromises between privacy protection and model performance.

Federated Learning (FL) has emerged as a promising solution by enabling model training across multiple decentralized institutions without directly sharing patient data. However, even in federated settings, model updates can potentially leak sensitive information through sophisticated attacks like model inversion or membership inference.

Diabetic retinopathy - a leading cause of preventable blindness globally - serves as an ideal test case for privacy-preserving AI development due to its high prevalence and the diagnostic challenges it presents, which require robust models trained on diverse patient populations.

## FedGAN: A Privacy-Preserving Framework for Medical Image Generation

To address these challenges, we developed FedGAN, a novel framework that combines Generative Adversarial Networks (GANs) with cross-silo federated learning for synthetic medical image generation. This approach allows multiple clinical institutions to collaboratively train a model that generates realistic retinal images while keeping patient data strictly private.

### Key Components of FedGAN:

1. **Data Preprocessing Pipeline**: A standardization process that prepares heterogeneous medical images for GAN training while preserving diagnostically relevant features
2. **Modified DCGAN Architecture**: Optimized for medical image generation, with specific adaptations for retinal imaging
3. **Transfer Learning Strategy**: A two-phase approach that leverages pretraining on a large anatomically similar dataset before federated fine-tuning
4. **Federated Learning Protocol**: A secure aggregation mechanism that enables collaborative model improvement without direct data sharing

## Datasets and Preprocessing

The research utilized two complementary datasets:

1. **RSNA Abdominal Trauma Detection Dataset**: ~3,000,000 grayscale CT images used for pretraining
2. **Diabetic Retinopathy Dataset**: 10,000 high-resolution retinal images with severity classifications (0-4)

![Sample RSNA Abdominal Trauma Dataset](static/RSNA_Sample.avif)
_Sample images from the RSNA Abdominal Trauma Dataset used for pretraining_

| Severity Level | Description                        | Example Retina Image                              |
| -------------- | ---------------------------------- | ------------------------------------------------- |
| 0              | No diabetic retinopathy            | ![No DR](static/no_dr.avif)                       |
| 1              | Mild diabetic retinopathy          | ![Mild DR](static/mild_dr.avif)                   |
| 2              | Moderate diabetic retinopathy      | ![Moderate DR](static/moderate_dr.avif)           |
| 3              | Severe diabetic retinopathy        | ![Severe DR](static/severe_dr.avif)               |
| 4              | Proliferative diabetic retinopathy | ![Proliferative DR](static/proliferative_dr.avif) |

_Diabetic Retinopathy Dataset with severity levels_

The comprehensive preprocessing pipeline included:

- Conversion to tensor format
- Resizing to 128x128 pixels
- Grayscale conversion
- CLAHE application for contrast enhancement
- Normalization to [0,1] range
- Gamma correction
- Pixel binning
- Rescaling to [-1,1]
- TFRecord storage for efficient processing

This pipeline ensured consistency, enhanced image quality, and standardized data format for optimal GAN training.

{{template:cta}}

## DCGAN Architecture

The generative model builds on the established DCGAN architecture with modifications specific to medical imaging. The generator and discriminator networks were carefully designed to balance image fidelity with computational efficiency.

![DCGAN Generator Architecture](static/DCGAN_Generator_Architecture.avif)
_The proposed DCGAN Generator Architecture_

![DCGAN Discriminator Architecture](static/DCGAN_Discriminator_Architecture.avif)
_The proposed DCGAN Discriminator Architecture_

Key modifications included:

- Optimized output resolution (128x128 pixels)
- Enhanced layer depth for capturing complex retinal patterns
- Comprehensive batch normalization for stable federated training

## The Federated Learning Approach

To simulate real-world clinical data distribution, we created a sophisticated partitioning strategy that mirrors how different medical institutions specialize in particular disease presentations. We systematically split the data by severity levels, assigning each label's cases to different clients to create a non-IID (non-Independent and Identically Distributed) data scenario.

The federated learning algorithm employed a three-step process:

1. **Pretraining**: The model was first trained on the large RSNA dataset to establish fundamental image generation capabilities
2. **Local Training**: Each client (clinical institution) trained the model on their private data
3. **Secure Aggregation**: Client models were averaged using FedAvg without sharing raw patient data

We evaluated different federation sizes (3, 5, 7, and 10 clients) to assess how the number of participants affects model performance and privacy preservation.

## Results and Analysis

The experiments demonstrated that FedGAN successfully generates realistic synthetic medical images while preserving patient privacy. The evaluation focused on both quantitative metrics (realism scores) and qualitative assessment of the generated images.

The realism scores for different client configurations were:

- 3 clients: 0.43
- 5 clients: 0.37
- 7 clients: 0.36
- 10 clients: 0.35

These scores indicate that smaller federations achieve performance closer to centralized training while maintaining privacy.

### Generator and Discriminator Loss Trends

The loss curves provide insights into training dynamics across different federation sizes:

| # of Clients | Generator Loss                                                      | Discriminator Loss                                                          |
| ------------ | ------------------------------------------------------------------- | --------------------------------------------------------------------------- |
| Unfederated  | ![Generator Loss](static/generator_loss.avif)                       | ![Discriminator Loss](static/discriminator_loss.avif)                       |
| 3 Clients    | ![Generator Loss 3 Clients](static/loss_generator_3_clients.avif)   | ![Discriminator Loss 3 Clients](static/loss_discriminator_3_clients.avif)   |
| 5 Clients    | ![Generator Loss 5 Clients](static/loss_generator_5_clients.avif)   | ![Discriminator Loss 5 Clients](static/loss_discriminator_5_clients.avif)   |
| 7 Clients    | ![Generator Loss 7 Clients](static/loss_generator_7_clients.avif)   | ![Discriminator Loss 7 Clients](static/loss_discriminator_7_clients.avif)   |
| 10 Clients   | ![Generator Loss 10 Clients](static/loss_generator_10_clients.avif) | ![Discriminator Loss 10 Clients](static/loss_discriminator_10_clients.avif) |

The unfederated model shows the most stable convergence, while among federated configurations, the 3-client setup achieved the closest approximation to centralized performance. As the number of clients increases, we observe more pronounced oscillations in loss values, reflecting the challenges of reconciling updates from more heterogeneous data sources.

### Sample Generated Images

The quality of synthetic images provides the most direct measure of model performance:

![Unfederated Sample](static/unfederated_sample.avif)
_Sample image from the unfederated (centralized) model_

| # of Clients | Generated Samples                                                         |
| ------------ | ------------------------------------------------------------------------- |
| 3 Clients    | ![Generated Samples 3 Clients](static/generated_samples_3_clients.avif)   |
| 5 Clients    | ![Generated Samples 5 Clients](static/generated_samples_5_clients.avif)   |
| 7 Clients    | ![Generated Samples 7 Clients](static/generated_samples_7_clients.avif)   |
| 10 Clients   | ![Generated Samples 10 Clients](static/generated_samples_10_clients.avif) |

Visual inspection confirms the quantitative findings, showing a gradual degradation in image fidelity as the number of clients increases. The 3-client configuration produces the most coherent and realistic synthetic images among the federated approaches.

## Key Insights and Trade-offs

The research revealed several important insights about privacy-preserving medical image generation:

1. **Privacy-Performance Trade-off**: While centralized training yields the highest visual fidelity, the federated approach successfully preserves patient privacy by eliminating direct data sharing. This represents a reasonable compromise for medical applications where privacy is paramount.

2. **Federation Size Impact**: Smaller federations (3-5 clients) achieve performance closer to centralized training, with the 3-client configuration reaching 86% of centralized performance while maintaining complete data isolation.

3. **Data Heterogeneity Challenges**: Non-IID data distribution affects performance consistency across clients, reflecting real-world clinical specialization patterns and highlighting the importance of effective heterogeneity handling in federated medical applications.

4. **Scalability Considerations**: Larger federations produce more consistent but slightly lower-quality synthetic images due to increased diversity and potential conflicts during update aggregation.

## Conclusion and Future Directions

FedGAN demonstrates that privacy-preserving synthetic medical image generation through federated GANs is not only feasible but can produce results that approach the quality of centralized training while maintaining strict data isolation. This achievement represents an important step toward enabling secure, collaborative AI development in healthcare settings without compromising patient confidentiality or regulatory compliance.

Future research directions include:

- **Quantifying Privacy Leakage**: Developing rigorous methodologies to measure and mitigate potential privacy risks in federated learning systems
- **Advanced Federated Algorithms**: Exploring more sophisticated federation techniques beyond basic FedAvg
- **Alternative Generative Models**: Investigating diffusion models and VAEs within the federated framework
- **Expanding to Other Imaging Tasks**: Extending the approach to segmentation, anomaly detection, and additional medical imaging modalities

By addressing these challenges, we can continue to advance the state of privacy-preserving medical AI, enabling healthcare institutions to collaborate on model development without compromising the sensitive patient data entrusted to their care.

---

_For technical details or to learn more about this project, you can view my complete research through my ORCID profile: 0009-0005-3034-1679._

---
