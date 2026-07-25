# Kurum Rehberi

**Kurum Rehberi**, NVDA ekran okuyucusu kullanıcıları için geliştirilmiş erişilebilir, sade, düzenli ve özelleştirilebilir bir kurum/personel rehberi eklentisidir.

Bu eklenti; kurumlarda görev yapan personelin ad, soyad, görev veya unvan, birim, telefon numarası, dahili numara, e-posta ve not bilgilerini düzenli biçimde kaydetmek, aramak, düzenlemek, yedeklemek ve gerektiğinde bu bilgilere hızlıca ulaşmak amacıyla hazırlanmıştır.

## Sürüm

```text
1.2.0
```

## Geliştirici

```text
Mehmet Aykurt
```

İletişim:

```text
m.aykurt38@gmail.com
```

## Genel Amaç

Kurum Rehberi’nin temel amacı, görme engelli NVDA kullanıcılarının kurum içi rehber bilgilerine bağımsız, hızlı, güvenilir ve düzenli biçimde erişebilmesini sağlamaktır.

Eklenti; santral görevlileri, memurlar, okul personeli, kurum çalışanları ve düzenli iletişim bilgisi tutmak isteyen NVDA kullanıcıları için pratik bir kayıt, arama, düzenleme ve yedekleme ortamı sunar.

## Başlıca Özellikler

- Yeni rehber kaydı oluşturma.
- Mevcut kayıtları düzenleme.
- Seçili kaydı silme.
- Rehber içinde hızlı arama yapma.
- Seçili kayıt bilgilerini ayrıntılı biçimde görüntüleme.
- Telefon numarası, dahili numara ve e-posta adresini hızlıca kopyalama.
- Kayıtları JSON biçiminde dışa aktarma.
- Daha önce alınmış JSON yedeklerini içe aktarma.
- İçe aktarma öncesinde mevcut kayıtların otomatik yedeğini alma.
- Görünecek alanları ayarlardan belirleme.
- Yardım dosyasına doğrudan eklenti penceresinden erişme.
- İleride farklı dillere çevrilebilmesi için hazırlanmış çeviri altyapısı.

## Sürüm 1.2.0 ile Gelen Düzenlemeler

- Çeşitli iyileştirmeler yapıldı.

## Kullanım

Eklenti varsayılan olarak aşağıdaki kısayol ile açılır:

```text
NVDA+Shift+R
```

Kullanıcı isterse bu kısayolu NVDA menüsünde yer alan **Tercihler > Girdi Hareketleri** bölümünden değiştirebilir.

Girdi Hareketleri bölümünde yalnızca Kurum Rehberi penceresini açan komut bulunur. Yeni kayıt, düzenleme, silme, ayarlar ve yardım gibi işlemlere ait kısayollar yalnızca Kurum Rehberi penceresi açıkken geçerlidir.

## Ana Pencere

Eklenti açıldığında ilk odak arama alanına gelir.

Ana pencerede sırasıyla şu bölümler yer alır:

- Arama alanı.
- Aramayı Temizle düğmesi.
- Kayıt listesi.
- Seçili kayıt bilgilerini gösteren salt okunur alanlar.
- İşlem düğmeleri.

Ana penceredeki işlem düğmeleri şunlardır:

- Yeni Kayıt.
- Düzenle.
- Sil.
- İçe/Dışa Aktar.
- Ayarlar.
- Yardım.
- Kapat.

## Klavye Kısayolları

Ana pencere açıkken kullanılabilecek temel kısayollar:

```text
Alt+Y: Yeni kayıt penceresini açar.
Alt+Z: Seçili kaydı düzenler.
Alt+S: Seçili kaydı silme işlemini başlatır.
Alt+A: İçe/Dışa Aktar penceresini açar.
Alt+R: Ayarlar penceresini açar.
Alt+H: Yardım dosyasını açar.
Alt+K: Kurum Rehberi penceresini kapatır.
```

Kayıt listesi üzerindeyken:

```text
Enter: Seçili kaydı düzenler.
Delete: Seçili kaydı silmek üzere onay penceresi açar.
```

Seçili kayıt bilgi alanlarında:

```text
Alt+C: Odaktaki bilgi alanının içeriğini panoya kopyalar.
Alt+T: Seçili kaydın telefon numarasını panoya kopyalar.
Alt+D: Seçili kaydın dahili numarasını panoya kopyalar.
Alt+E: Seçili kaydın e-posta adresini panoya kopyalar.
```

## Ayarlar

Ayarlar penceresinde kayıt alanlarının görünürlüğü değiştirilebilir.

Açılıp kapatılabilen alanlar:

- Ad.
- Soyad.
- Görev/Unvan.
- Birim.
- Telefon Numarası.
- Dahili Numara.
- E-posta.
- Not.

Bir alanın kapatılması mevcut kayıt verilerini silmez. Kapatılan alan yalnızca ana listede, yeni kayıt penceresinde, düzenleme penceresinde, seçili kayıt bilgilerinde ve arama kapsamında gizlenir. Alan yeniden açıldığında daha önce kaydedilmiş bilgiler tekrar görünür.

Kurum Rehberi penceresi açıkken ayarlar değiştirilirse, değişikliklerin uygulanması için Kurum Rehberi penceresinin kapatılıp yeniden açılması gerekir.

## İçe Aktarma ve Dışa Aktarma

Dışa aktarma işlemi, mevcut rehber kayıtlarını kullanıcının Belgeler klasörüne JSON biçiminde yedek dosyası olarak kaydeder.

İçe aktarma işlemi, daha önce oluşturulmuş bir JSON yedek dosyası seçilerek rehber kayıtlarının geri yüklenmesini sağlar. İşlem başlamadan önce kullanıcıdan onay alınır.

İçe aktarma sırasında mevcut kayıtların otomatik yedeği alınır. Böylece yanlış dosya seçilmesi veya beklenmeyen bir durum yaşanması hâlinde önceki kayıtların geri alınabilmesi kolaylaşır.

## Verilerin Saklanması

Eklenti kayıtları, kullanıcının NVDA yapılandırma klasörü içinde yer alan aşağıdaki klasörde saklanır:

```text
kurum_rehberi
```

Kayıt dosyası:

```text
rehber.json
```

Ayar dosyası:

```text
ayarlar.json
```

## Gizlilik

Kurum Rehberi; kişisel verileri, rehber kayıtlarını, ayar bilgilerini veya kullanım verilerini kendiliğinden internet üzerinden herhangi bir sunucuya göndermez.

Eklenti, rehber verilerini yalnızca kullanıcının kendi bilgisayarında yerel olarak saklar. Kayıtlar; görüntüleme, düzenleme, arama, silme, içe aktarma ve dışa aktarma işlemleri dışında herhangi bir amaçla kullanılmaz.

## Çeviri Katkıları

Kurum Rehberi Türkçe olarak hazırlanmıştır. Bununla birlikte, ileride farklı dillere çevrilebilmesi için eklenti metinleri çeviriye uygun biçimde düzenlenmiştir.

Çeviri yapmak isteyenler için çeviri şablonu ve başlangıç dosyaları sağlanabilir.

Temel çeviri dosyaları:

```text
po/kurum_rehberi.pot
locale/en/LC_MESSAGES/nvda.po
```

Çeviri yapılırken:

- `msgid` satırları değiştirilmemelidir.
- Yalnızca `msgstr` alanları çevrilmelidir.
- `&` işareti erişim tuşunu belirtir; hedef dilde uygun harfin önüne taşınabilir.
- `{0}`, `{1}` gibi yer tutucular aynen korunmalıdır.

Tamamlanmış çeviri, derlenmiş `nvda.mo` dosyası olarak ilgili dil klasörüne eklenir.

Örnek:

```text
locale/en/LC_MESSAGES/nvda.mo
```

## Yardım Dosyası

Ayrıntılı kullanım ve bilgilendirme kılavuzu eklenti içinde şu konumda yer alır:

```text
doc/tr/readme.html
```

NVDA içinden Yardım düğmesine basıldığında bu dosya açılır.

## Lisans

Bu eklenti **GNU General Public License v2.0** kapsamında lisanslanmıştır.

Eklentiyi değiştiren, uyarlayan veya yeniden dağıtan kişiler, lisans hükümleri uyarınca özgün geliştirici bilgisini, telif bildirimini ve lisans bilgisini korumalıdır.

## Telif ve Geliştirici Bildirimi

```text
Telif hakkı © 2026 Mehmet Aykurt
```

Kurum Rehberi, Mehmet Aykurt tarafından geliştirilmiştir.

Bu eklentinin değiştirilmiş sürümleri dağıtılırken yapılan değişikliklerin açıkça belirtilmesi ve özgün çalışmanın Mehmet Aykurt tarafından geliştirildiği bilgisinin korunması gerekir.

## Son Söz

Kurum Rehberi; sade görünümü, erişilebilir yapısı ve özelleştirilebilir alanlarıyla farklı kullanım senaryolarına uyum sağlayacak biçimde tasarlanmıştır. Temel hedef, NVDA kullanıcılarının iletişim bilgilerine daha hızlı, düzenli ve bağımsız biçimde ulaşabilmesini sağlamaktır.
