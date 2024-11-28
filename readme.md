
# **Archive Records Digitization System (ARDS)**  
**Enhancing Security and Efficiency in University Archives through OCR-CNN Digitization**

## **Overview**
The Archive Records Digitization System (ARDS) is a cutting-edge web-based application that revolutionizes the digitization of academic records. By leveraging Optical Character Recognition (OCR) technology enhanced with Convolutional Neural Networks (CNNs), ARDS converts physical documents into editable, searchable digital formats. This system addresses challenges like diverse document layouts, varying text quality, and security risks. Specifically designed for the University of Southeastern Philippines – Office of the University Registrar (UseP-OUR), ARDS sets a new standard for academic record management.

## **Key Features**
- **Advanced OCR-CNN Integration**: Combines OCR technology with CNNs for superior text recognition accuracy, even in complex document layouts and degraded text quality.  
- **Digital Archiving**: Digitizes paper-based records into secure, encrypted digital formats.  
- **Data Security**: Utilizes robust encryption protocols like AES-CBC to protect sensitive student data.  
- **Efficient Data Management**: Streamlines document handling with automated tagging, validation, and structuring of extracted data.  
- **User-Centric Design**: Offers an intuitive web interface for uploading, managing, and accessing digitized records.  
- **Time Efficiency**: Reduces the average processing time per document to just 2 minutes.  
- **Offline Functionality**: Operates in secure offline environments, minimizing cybersecurity risks.  

## **Purpose**
ARDS addresses the limitations of manual record-keeping by providing a secure, efficient, and ergonomic solution for academic institutions. It safeguards student records, streamlines operations, and ensures long-term data accessibility while reducing operational vulnerabilities and risks associated with physical storage.

## **Technical Architecture**
1. **Image Preprocessing**: Enhances document quality for optimal text recognition.  
2. **OCR and CNN Integration**: Extracts and processes text using deep learning models tailored to academic record formats.  
3. **Database Interaction**: Validates and stores structured data in an encrypted, centralized database.  
4. **Interactive Dashboard**: Displays digitized records and analytics for administrative use.

## **Tools and Technologies**
- **Flask**: Backend framework for web development.  
- **PaddleOCR and YOLO**: Advanced OCR and table detection tools.  
- **AES Encryption**: Ensures data security.  
- **Agile Methodology**: Employed for iterative design, testing, and deployment.

---

## **Installation Instructions**

### **1. Clone the Repository**
```bash
git clone https://github.com/r-limpz/archival-system.git
```

### **2. Install Dependencies**
Ensure Python 3.x is installed. Then, install the required libraries:
```bash
pip install -r requirements.txt
```

### **3. Model Setup**
- Follow the [PaddleOCR Installation Guide](https://github.com/PaddlePaddle/PaddleOCR/blob/main/README_en.md).  
- Set up YOLO for table detection using [these instructions](https://huggingface.co/foduucom/table-detection-and-extraction).

### **4. Configure the Server**
Ensure the `serve.py` script is correctly set up to launch the Flask server.

---

## **Running the Application**

1. **Start the Server**  
   Execute the `serve.py` script to initialize the application:
   ```bash
   python serve.py
   ```

2. **Access the Dashboard**  
   Open your web browser and navigate to:
   ```text
   http://127.0.0.1:8080
   ```

---

## **Comparative Analysis**
### **Performance Metrics**
| **Method**           | **Average Time/Document** | **Character Error Rate (CER)** |
|-----------------------|---------------------------|---------------------------------|
| Traditional Archiving | 8 minutes                | N/A                             |
| OCR                  | 6 minutes                | 10–30%                         |
| OCR-CNN              | 2 minutes                | 0–20%                          |

---

Acknowledgments
This project was made possible through the collaborative efforts of:

Adviser: Dr. Maureen M. Villamor
Faculty and staff of the College of Information and Computing, USeP
Panelists: Nancy S. Mozo, MIT, and Leah O. Pelias, DBM-IS
Special thanks to the developers for their contributions:

- Ken Jerold Y. Arellano: Project Manager and Assistant Back-End Developer
- Rex Xyriel R. Limpangog: Programming Lead
- Earl Lemuel S. Egos: Technical Writer

---

### **Future Directions**
1. **Expand Document Support**: Incorporate multilingual and multi-format capabilities.  
2. **Enhance Security**: Develop additional encryption layers and authentication methods.  
3. **Integrate NLP**: Utilize Natural Language Processing for better categorization and context extraction.

