from wa_infra_tools.database import PostgresDatabase

db = PostgresDatabase("bhu49", "tux-144.cae.wisc.edu")
db.join_and_download_data("test_images", "test_bb_labels", ["class_id", "center_norm_x", "center_norm_y", "height_norm", "width_norm"], "test", "yolo")
