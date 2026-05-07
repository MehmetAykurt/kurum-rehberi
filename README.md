Kurum Rehberi Kullanım ve Bilgilendirme Kılavuzu

Eklentinin Adı: Kurum Rehberi

Güncelleme Tarihi: 7 Mayıs 2026

Hazırlayan: Mehmet Aykurt

İletişim E-postası: m.aykurt38@gmail.com

Genel Tanıtım

Kurum Rehberi, NVDA ekran okuyucusu kullanıcıları için hazırlanmış erişilebilir, sade, kullanışlı ve özelleştirilebilir bir rehber eklentisidir. 

Bu eklenti; kurumlarda görev yapan personelin ad, soyad, görev veya unvan, birim, telefon numarası, dahili numara, e-posta ve not bilgilerini düzenli biçimde kaydetmek ve bu bilgilere hızlıca ulaşmak amacıyla geliştirilmiştir. 

Eklenti varsayılan olarak kurum personeli ve kurum içi iletişim bilgileri için tasarlanmıştır. Bununla birlikte, ayarlar bölümünde yer alan alan görünürlüğü seçenekleri sayesinde farklı kullanım ihtiyaçlarına göre sadeleştirilebilir. Kullanıcı, ihtiyaç duymadığı alanları kapatarak eklentiyi yalnızca telefon rehberi, e-posta rehberi veya kişisel iletişim rehberi olarak da kullanabilir. 

Temel Amaç

Kurum Rehberi’nin temel amacı, görme engelli kullanıcıların kurum içi rehber bilgilerine bağımsız, hızlı ve güvenilir biçimde erişmesini sağlamaktır. Eklenti, ekran okuyucu kullanımına uygun biçimde tasarlanmış olup klavye ile rahatça kullanılabilir. 

Santral görevlileri, memurlar, okul personeli, kurum çalışanları ve düzenli iletişim bilgisi tutmak isteyen NVDA kullanıcıları için pratik bir kayıt ve erişim ortamı sunar. 

Başlıca Özellikler

Eklenti ile yeni kayıt oluşturulabilir, mevcut kayıtlar düzenlenebilir, kayıtlar silinebilir, rehber içinde arama yapılabilir, kayıt bilgileri hızlıca kopyalanabilir, veriler dışa aktarılabilir ve daha önce alınmış yedekler içe aktarılabilir. 

Kayıtlar ad ve soyad bilgisine göre otomatik olarak sıralanır. Arama alanına yazılan metin, ayarlarda görünür durumda olan alanlar içinde aranır. Arama alanı temizlendiğinde tüm kayıtlar yeniden listelenir. 

Kullanım

Eklenti varsayılan olarak NVDA+Shift+R kısayolu ile açılır. Kullanıcı isterse bu kısayolu NVDA menüsünde yer alan Tercihler, Girdi Hareketleri bölümünden değiştirebilir. 

Eklenti ayrıca NVDA Araçlar menüsündeki Kurum Rehberi alt menüsünde yer alır. Bu menüden Kurum Rehberi’ni Aç, Ayarlar ve Yardım seçeneklerine ulaşılabilir. 

Eklenti açıldığında ilk odak arama alanına gelir. Kullanıcı doğrudan aramak istediği adı, soyadı, birimi, görevi, telefon numarasını, dahili numarayı, e-posta adresini veya not bilgisini yazabilir. 

Klavye Kullanımı

Liste üzerindeyken Enter tuşu seçili kaydı düzenler. Delete tuşu, seçili kaydı silmek üzere onay penceresi açar. Alt+S seçili kaydı silme işlemini başlatır. 

Seçili kayıt bilgi alanlarından birindeyken Alt+C, o alanın içeriğini panoya kopyalar. Alt+T seçili kaydın telefon numarasını, Alt+D dahili numarasını, Alt+E ise e-posta adresini doğrudan kopyalar. 

Ayarlar

Ayarlar bölümünde kayıt alanlarının görünürlüğü değiştirilebilir. Ad, soyad, görev veya unvan, birim, telefon numarası, dahili numara, e-posta ve not alanları onay kutuları aracılığıyla açılıp kapatılabilir. 

Varsayılan olarak tüm alanlar görünür durumdadır. Kullanıcı, ihtiyaç duymadığı alanların işaretini kaldırarak arayüzü sadeleştirebilir. 

Bir alanın kapatılması mevcut kayıt verilerini silmez. Kapatılan alan yalnızca ana listede, yeni kayıt penceresinde, düzenleme penceresinde, seçili kayıt bilgilerinde ve arama kapsamında gizlenir. Alan yeniden açıldığında daha önce kaydedilmiş bilgiler tekrar görünür. 

Kurum Rehberi penceresi açıkken ayarlar değiştirilirse, değişikliklerin uygulanması için Kurum Rehberi penceresinin kapatılıp yeniden açılması gerekir. 

Verilerin Saklanması

Eklenti kayıtları, kullanıcının NVDA yapılandırma klasörü içinde yer alan kurum\_rehberi klasöründe saklanır. Kayıt dosyası rehber.json adını taşır. 

Ayarlar, aynı klasörde bulunan ayarlar.json dosyasında tutulur. 

İçe Aktarma ve Dışa Aktarma

Dışa aktarma işlemi, mevcut rehber kayıtlarını kullanıcının Belgeler klasörüne yedek dosyası olarak kaydeder. Yedek dosyası, tarih ve saat bilgisi içeren bir dosya adıyla oluşturulur. 

İçe aktarma işlemi, daha önce oluşturulmuş bir JSON yedek dosyası seçilerek rehber kayıtlarının geri yüklenmesini sağlar. İşlem başlamadan önce kullanıcıdan onay alınır. Bu işlem, mevcut rehber kayıtlarının yerine seçilen yedek dosyasındaki kayıtları getirir. 

İçe aktarma sırasında güvenlik amacıyla mevcut kayıtların otomatik yedeği alınır. Böylece yanlış dosya seçilmesi veya beklenmeyen bir durum yaşanması hâlinde, önceki kayıtların geri alınabilmesi kolaylaşır. 

Gizlilik ve Yerel Saklama

Kurum Rehberi; kişisel verileri, rehber kayıtlarını, ayar bilgilerini veya kullanım verilerini internet üzerinden herhangi bir sunucuya göndermez. 

Eklenti herhangi bir çevrim içi hizmete bağlanmaz; veri toplamaz, takip yapmaz, analiz veya istatistik amacıyla bilgi işlemez. Tüm kayıtlar ve ayarlar yalnızca kullanıcının kendi bilgisayarında yerel olarak saklanır. 

Kullanıcı tarafından girilen rehber bilgileri tamamen kullanıcının sorumluluğundadır. Eklenti bu bilgileri yalnızca yerel kayıt, görüntüleme, düzenleme, arama, içe aktarma ve dışa aktarma işlemleri için kullanır. 

Erişilebilirlik

Eklenti, NVDA ekran okuyucusu ile kullanılmak üzere hazırlanmıştır. Arayüzdeki alanlar, düğmeler, listeler ve bilgi alanları klavye ile erişilebilir olacak şekilde düzenlenmiştir. 

Seçili kayıt bilgileri, ekran okuyucu ile rahat takip edilebilmesi için ayrı bilgi alanlarında gösterilir. Kullanıcı, Tab ve Shift+Tab tuşlarıyla alanlar arasında gezinebilir. 

Öneri, Görüş ve Eleştiriler

Kurum Rehberi’nin geliştirme süreci, kullanıcı deneyimleri ve gerçek ihtiyaçlar doğrultusunda sürdürülecektir. Her türlü öneri, görüş ve eleştiri için Mehmet Aykurt ile aşağıdaki e-posta adresi üzerinden iletişime geçilebilir. 

E-posta: m.aykurt38@gmail.com

Telif, Lisans ve Özgün Geliştirici Bildirimi

Kurum Rehberi, Mehmet Aykurt tarafından geliştirilmiştir. 

Telif hakkı © 2026 Mehmet Aykurt. Öneri, görüş ve eleştiriler için m.aykurt38@gmail.com adresi üzerinden iletişime geçilebilir. 

Bu eklenti GNU General Public License v2.0 kapsamında lisanslanmıştır. Eklentiyi değiştiren, uyarlayan veya yeniden dağıtan kişiler, lisans hükümleri uyarınca özgün geliştirici bilgisini, telif bildirimini ve lisans bilgisini korumalıdır. 

Bu eklentinin değiştirilmiş sürümleri dağıtılırken yapılan değişikliklerin açıkça belirtilmesi ve özgün çalışmanın Mehmet Aykurt tarafından geliştirildiği bilgisinin korunması gerekir. 

Son Söz

Kurum Rehberi; sade görünümü, erişilebilir yapısı ve özelleştirilebilir alanlarıyla farklı kullanım senaryolarına uyum sağlayacak biçimde tasarlanmıştır. Temel hedef, NVDA kullanıcılarının iletişim bilgilerine daha hızlı, düzenli ve bağımsız biçimde ulaşabilmesini sağlamaktır. 

