# maven 依赖

     <!-- https://mvnrepository.com/artifact/org.apache.poi/poi -->
    <dependency>
        <groupId>org.apache.poi</groupId>
        <artifactId>poi</artifactId>
        <version>4.1.2</version>
    </dependency>

    <!-- https://mvnrepository.com/artifact/org.apache.poi/poi-ooxml -->
    <dependency>
        <groupId>org.apache.poi</groupId>
        <artifactId>poi-ooxml</artifactId>
        <version>4.1.2</version>
    </dependency>

# 代码

    import org.apache.pdfbox.cos.COSName;
    import org.apache.pdfbox.pdmodel.PDDocument;
    import org.apache.pdfbox.pdmodel.PDPage;
    import org.apache.pdfbox.pdmodel.PDResources;
    import org.apache.pdfbox.pdmodel.graphics.image.PDImageXObject;
    import org.apache.pdfbox.rendering.ImageType;
    import org.apache.pdfbox.rendering.PDFRenderer;
    import org.apache.poi.sl.usermodel.PictureData;
    import org.apache.poi.xslf.usermodel.XMLSlideShow;
    import org.apache.poi.xslf.usermodel.XSLFPictureShape;

    import javax.imageio.ImageIO;
    import java.awt.*;
    import java.awt.image.BufferedImage;
    import java.io.ByteArrayInputStream;
    import java.io.ByteArrayOutputStream;
    import java.io.File;
    import java.io.FileOutputStream;
    import java.io.IOException;

    /**
     * @author Maning
     */
    public class Domain {
        public static void main(String[] args) throws IOException {
            File pdfFile = new File("F:\\房地产策划的物料系统.pdf");
            PDDocument pdf = PDDocument.load(pdfFile);
            XMLSlideShow ppt = new XMLSlideShow();
            // 可选设置ppt大小,默认720*540
             ppt.setPageSize(new Dimension(1280, 720));

            // 将pdf渲染成图片再进行转换,兼容性更好
            turnAsImg(pdf, ppt);
            // 纯扫描pdf转换,直接取出原图进行转换,质量更好,非扫描pdf会丢失文字内容
            // turnOnlyImg(pdf, ppt);
            // 提取图片
            // extractImg("D:/1.pdf");

            ppt.write(new FileOutputStream(pdfFile.getParent() + File.separatorChar + pdfFile.getName() + "转换的PPT文件.pptx"));
        }

        private static void turnAsImg(PDDocument pdf, XMLSlideShow ppt) throws IOException {
            PDFRenderer render = new PDFRenderer(pdf);
            int count = pdf.getNumberOfPages();
            for (int i = 0; i < count; i++) {
                imgInsertPdf(ppt, render.renderImageWithDPI(i, 300, ImageType.RGB));
            }
        }

        private static void turnOnlyImg(PDDocument pdf, XMLSlideShow ppt) throws IOException {
            for (PDPage page : pdf.getPages()) {
                PDResources resources = page.getResources();
                for (COSName cos : resources.getXObjectNames()) {
                    if (resources.isImageXObject(cos)) {
                        PDImageXObject obj = (PDImageXObject) resources.getXObject(cos);
                        imgInsertPdf(ppt, obj.getImage());
                    }

                }
            }
        }

        private static void imgInsertPdf(XMLSlideShow ppt, BufferedImage img) throws IOException {
            ByteArrayOutputStream bs = new ByteArrayOutputStream();
            ImageIO.write(img, "jpg", bs);
            XSLFPictureShape shape = ppt.createSlide().createPicture(ppt.addPicture(new ByteArrayInputStream(bs.toByteArray()), PictureData.PictureType.JPEG));
            shape.setAnchor(new Rectangle(0, 0, ppt.getPageSize().width, ppt.getPageSize().height));
        }

        private static void extractImg(String pdfPath) throws IOException {
            File pdfFile = new File(pdfPath);
            File dir = new File(pdfFile.getParent() + File.separatorChar + pdfFile.getName() + "提取的图片文件");
            if (dir.mkdirs()) {
                PDDocument pdf = PDDocument.load(pdfFile);
                int index = 1;
                for (PDPage page : pdf.getPages()) {
                    PDResources resources = page.getResources();
                    for (COSName cos : resources.getXObjectNames()) {
                        if (resources.isImageXObject(cos)) {
                            PDImageXObject obj = (PDImageXObject) resources.getXObject(cos);
                            ImageIO.write(obj.getImage(), "jpg", new File(dir.getPath() + File.separatorChar + index++ + ".jpg"));
                        }

                    }
                }
            }

        }

    }
