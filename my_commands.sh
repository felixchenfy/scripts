
/home/feiyu/workplace/scripts/convert_heic_to_jpg_images_and_rename.sh /home/feiyu/Downloads/1 day_1_2_

/home/feiyu/workplace/scripts/convert_heic_to_jpg_images_and_rename.sh /home/feiyu/Downloads/3 day_3_

/home/feiyu/workplace/scripts/convert_heic_to_jpg_images_and_rename.sh /home/feiyu/Downloads/4 day_4_5_

cp /home/feiyu/Downloads/1/* /home/feiyu/Downloads/汇总/
cp /home/feiyu/Downloads/3/* /home/feiyu/Downloads/汇总/
cp /home/feiyu/Downloads/4/* /home/feiyu/Downloads/汇总/

/home/feiyu/workplace/scripts/rename_files_with_image_creation_time.sh /home/feiyu/Downloads/汇总

/home/feiyu/workplace/scripts/set_dummy_date_for_sorted_image_files.sh /home/feiyu/Downloads/汇总
