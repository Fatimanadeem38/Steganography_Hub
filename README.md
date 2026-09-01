🔐 Steganography Hub

Steganography Hub is a secure web-based image steganography platform developed using Django and Digital Image Processing (DIP) techniques.

The system enables users to hide encrypted secret messages inside digital images and securely recover them using controlled key-based authentication.

The project combines image steganography, cryptography, digital image processing, and security mechanisms to provide a practical framework for secure information hiding.

---

🚀 Key Features

- Secure secret-message embedding inside images
- Edge-based image steganography
- Pixel and bit-level data embedding
- Secret key and image key generation
- Image ID-based message retrieval
- Secure message decoding
- Temporary lock after repeated incorrect attempts
- Image freezing after excessive failed attempts
- Authorized credential recovery
- Email-based account activation
- User authentication and access control
- Image quality and steganography evaluation
- Dedicated Digital Image Processing techniques module

---

🧠 Digital Image Processing

The system applies several Digital Image Processing concepts during image analysis and steganographic embedding, including:

- Spatial Domain Processing
- Edge-Based Embedding
- Pixel-Level Manipulation
- Bit-Level / LSB-Style Embedding
- Edge Detection
- Canny Edge Detection
- Feature Detection
- Neighborhood Operations
- Convolution
- Filtering
- Gradient-Based Analysis
- Partial Image Segmentation
- OpenCV-Based Image Processing

These techniques help identify suitable image regions and support secure message embedding while minimizing visible distortion.

---

🔒 Security Mechanisms

Steganography Hub incorporates multiple security layers beyond basic message hiding.

🔑 Key-Based Protection

Access to hidden information requires valid credentials associated with the encoded image.

⚠️ Failed Attempt Protection

Repeated incorrect decoding attempts are recorded and restricted.

⏳ Temporary Lock

After multiple incorrect attempts, decoding is temporarily blocked.

🔐 Image Freeze

Excessive unauthorized attempts can freeze access to an encoded image until authorized recovery is performed.

🔓 Secure Recovery

Authorized mechanisms allow legitimate users to recover access when required.

---

🔄 System Workflow

```text
User Registration / Login
          ↓
Select Cover Image
          ↓
Enter Secret Message
          ↓
Image Analysis & Edge Detection
          ↓
Message Encryption
          ↓
Steganographic Embedding
          ↓
Encoded Image Generation
          ↓
Image ID + Security Credentials
          ↓
Secure Sharing
          ↓
Receiver Enters Image ID + Secret Key
          ↓
Credential Verification
          ↓
Hidden Message Extraction
```

---

🧪 Research & Experimental Evaluation

The project has also been evaluated experimentally to study the behavior and effectiveness of the proposed steganography approach.

The experiments directory contains experimental results associated with the research evaluation.

Experiments include:

1. Dataset Capacity Analysis
2. Imperceptibility Evaluation
3. Payload Sensitivity Analysis
4. Edge-Based vs LSB Comparison
5. Edge Localization Analysis
6. Grouped Steganalysis
7. Final Corrected Rerun Summary

These experiments investigate image quality, embedding capacity, payload behavior, localization, comparative performance, and steganalysis characteristics.

---

📊 Evaluation Metrics

The experimental evaluation considers metrics such as:

- Mean Squared Error (MSE)
- Peak Signal-to-Noise Ratio (PSNR)
- Structural Similarity Index (SSIM)
- Embedding Capacity
- Payload Sensitivity
- Steganalysis / Detectability
- Edge Localization

---

📁 Repository Structure

```text
Steganography_Hub/
│
├── experiments/
│   ├── Corrected_Dataset_Capacity.xlsx
│   ├── Experiment1_CORRECTED_Imperceptibility.xlsx
│   ├── Experiment2_CORRECTED_Payload_Sensitivity.xlsx
│   ├── Experiment3_CORRECTED_BitMatched_Edge_vs_LSB.xlsx
│   ├── Experiment4_CORRECTED_Edge_Localization.xlsx
│   ├── Experiment5_CORRECTED_Grouped_Steganalysis.xlsx
│   └── FINAL_CORRECTED_RERUN_SUMMARY.xlsx
│
├── templates/
├── static/
├── media/
├── manage.py
├── requirements.txt
└── README.md
```

---

🛠️ Technologies Used

Backend
- Python
- Django

Frontend
- HTML5
- CSS3
- Bootstrap
- JavaScript

Image Processing
- OpenCV
- Digital Image Processing techniques

Security
- Cryptographic message protection
- Key-based verification
- Authentication
- Failed-attempt monitoring
- Temporary locking and image freezing

Research & Analysis
- Python-based experimentation
- Image-quality evaluation
- Comparative steganography analysis

---

⚙️ Installation

Clone the repository:

```bash
git clone https://github.com/Fatimanadeem38/Steganography_Hub.git
```

Move into the project directory:

```bash
cd Steganography_Hub
```

Create a virtual environment:

```bash
python -m venv env
```

Activate it on Windows:

```bash
env\Scripts\activate
```

Install the required dependencies:

```bash
pip install -r requirements.txt
```

Run database migrations:

```bash
python manage.py migrate
```

Start the Django development server:

```bash
python manage.py runserver
```

---

🎯 Project Objectives

- Develop a practical secure image-steganography platform
- Integrate Digital Image Processing with information security
- Reduce perceptible changes caused by secret-message embedding
- Protect hidden information against unauthorized access
- Analyze the effect of payload size and embedding strategy
- Evaluate steganographic images using quantitative metrics
- Study the detectability of embedded information
- Provide a usable web interface for secure encoding and decoding

---

🔬 Research Work

This software project is accompanied by experimental research investigating the performance and security characteristics of the implemented steganography approach.

The experimental files available in the experiments directory provide supporting results for the research study.

📄 Publication Status: Research manuscript prepared based on this project. Publication information will be added when available.

---

⚠️ Disclaimer

This project was developed for academic, research, and educational purposes. It demonstrates concepts related to image steganography, Digital Image Processing, cryptography, and secure information hiding.

---

👩‍💻 Author

Fatima Nadeem

BS Computer Science

Cybersecurity • Artificial Intelligence • Digital Image Processing
